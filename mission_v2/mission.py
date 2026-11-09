"""Shared mission geometry, observation semantics and external reference objective.

The fast service model is an explicit engineering abstraction for development;
its outputs are never labelled as ns-3/NR packet measurements.
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "config.json").read_text())
NAMES = ("nr", "lte", "wifi")
FEATURES = ("sinr_db", "rx_dbm", "delay_ms", "capacity_mbps", "loss")


def motion(t):
    """Continuous velocity, 1 s ramps at t=19.5 and 29.5; return x,v."""
    if t < 19.5:
        return 1600 - 30*t, 30.0
    if t < 20.5:
        u = t - 19.5
        return 1015 - 30*u + 12.5*u*u, 30 - 25*u
    if t < 29.5:
        return 997.5 - 5*(t-20.5), 5.0
    if t < 30.5:
        u = t - 29.5
        return 952.5 - 5*u - 10*u*u, 5 + 20*u
    return 937.5 - 25*(t-30.5), 25.0


def demand_at(x, config=CONFIG):
    imaging = 950 <= x <= 1000
    return config["imaging_mbps"] if imaging else config["preview_mbps"]


def sanitize(metrics):
    """Use a conservative missing-delay representation; never invent low delay."""
    x = np.array(metrics, dtype=np.float64, copy=True)
    x[..., 0] = np.nan_to_num(x[..., 0], nan=-40).clip(-50, 80)
    x[..., 1] = np.nan_to_num(x[..., 1], nan=-150).clip(-180, -10)
    x[..., 2] = np.nan_to_num(x[..., 2], nan=1000, posinf=1000).clip(0, 1000)
    x[..., 3] = np.nan_to_num(x[..., 3], nan=0).clip(0, 200)
    x[..., 4] = np.nan_to_num(x[..., 4], nan=1).clip(0, 1)
    return x


def features(metrics, demand):
    """Fixed physical transforms for ranking, shared by every method.

    These are engineering utility scales, not fitted forecast standardization.
    MLP/LSTM standardization is separately fitted on training missions only.
    """
    x = sanitize(metrics)
    req = np.asarray(demand)[..., None]
    return np.stack(((x[..., 0]+10)/40, (x[..., 1]+120)/70,
                     np.exp(-x[..., 2]/50),
                     np.minimum(x[..., 3]/np.maximum(req, .064), 1),
                     1-x[..., 4]), axis=-1).clip(0, 1)


def task_value(metrics, demand):
    """External expected on-time service in a memoryless, fresh-cohort model.

    Independent of TOPSIS/attention: telemetry gets strict priority; residual
    capacity serves video. Delay is deterministic per cohort in this model.
    Queueing packet-level evaluation is separate and does not inherit this
    model's optimality guarantee. Demand is video load in Mbps.
    """
    x = sanitize(metrics)
    cap = x[..., 3]
    telemetry = np.minimum(cap/.064, 1)*(x[..., 2] <= 50)*(1-x[..., 4])
    video = np.minimum(np.maximum(cap-.064, 0)/np.maximum(np.asarray(demand)[..., None], .001), 1)
    video *= (x[..., 2] <= 200)*(1-x[..., 4])
    return 4*telemetry + video


def abstract_trace(seed, stress=0.0, config=CONFIG):
    """Distance/link-budget based development trace; no prescribed scores/order."""
    rng = np.random.default_rng(seed)
    dt = config["period_s"]
    times = np.arange(0, config["duration_s"]-dt/2, dt)
    jitter = np.r_[rng.uniform(-30, 30, 2), rng.uniform(-10, 10)]
    xyv = np.array([motion(t) for t in times])
    positions = np.column_stack((xyv[:, 0]+jitter[0], np.full(len(times), 1000+jitter[1]),
                                 np.full(len(times), 100+jitter[2])))
    demand = np.array([demand_at(p[0], config) for p in positions])
    dist = np.linalg.norm(positions[:, None]-np.array(config["sites"])[None], axis=-1).clip(1)
    # Link budgets: radiated power, reference loss at 1 m, exponent and receiver noise.
    tx = np.array([23, 23, 20]); ref = np.array(config['reference_loss_db']); exponent = np.array(config['pathloss_exponents'])
    noise = np.array([-94, -100, -94]); rx = tx-ref-10*exponent*np.log10(dist)
    # Same explicit geometric obstruction hypothesis as the actual PHY model.
    bounds=np.array(config['building_bounds_m'])
    for n,site in enumerate(config['sites']):
        delta=np.array(site)-positions;enter=np.zeros(len(times));leave=np.ones(len(times));cross=np.ones(len(times),dtype=bool)
        for k in range(3):
            moving=np.abs(delta[:,k])>1e-9
            first=np.divide(bounds[k,0]-positions[:,k],delta[:,k],out=np.full(len(times),-np.inf),where=moving)
            last=np.divide(bounds[k,1]-positions[:,k],delta[:,k],out=np.full(len(times),np.inf),where=moving)
            enter=np.maximum(enter,np.minimum(first,last));leave=np.minimum(leave,np.maximum(first,last))
            cross&=moving|((positions[:,k]>=bounds[k,0])&(positions[:,k]<=bounds[k,1]))
        cross&=(enter<=leave)&(leave>=0)&(enter<=1)
        rx[:,n]-=cross*config['obstruction_loss_db']
    fading = np.zeros_like(rx)
    innovations = rng.normal(0, stress, rx.shape)
    for k in range(1, len(times)):
        fading[k] = .85*fading[k-1] + np.sqrt(1-.85**2)*innovations[k]
    rx += fading
    sinr = rx-noise
    bandwidth = np.array([20, 10, 20])
    efficiency = np.array([.55, .35, .45])
    capacity = bandwidth*efficiency*np.log2(1+10**(sinr/10))
    # LTE's declared backhaul is a real configurable resource bottleneck.
    capacity[:, 1] = np.minimum(capacity[:, 1], 6.0)
    loss = 1/(1+np.exp((sinr+3)/1.5))
    capacity *= 1-loss
    delay = np.broadcast_to(np.array([5., 12., 3.]), rx.shape).copy()
    delay[capacity < .064] = 1000
    metrics = np.stack((sinr, rx, delay, capacity, loss), axis=-1)
    return {"time":times, "position":positions, "speed":xyv[:, 1], "demand":demand,
            "metrics":sanitize(metrics), "seed":seed, "backend":"service-abstraction"}


def save_trace(path, trace):
    np.savez_compressed(path, **trace)


def load_trace(path):
    with np.load(path, allow_pickle=False) as data:
        return {k:data[k] for k in data.files}
