"""Build an evidence-matched manuscript draft; preserve the submitted source."""
import json,re,shutil,subprocess
from pathlib import Path
import pandas as pd
from mission import ROOT,CONFIG


def main():
    source=ROOT.parent/'vehicular_communications_submission';out=ROOT/'manuscript_revision';out.mkdir(exist_ok=True)
    for f in ['elsarticle.cls','elsarticle-num.bst']:shutil.copy2(source/f,out/f)
    (out/'Figures').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'figures/fig1_mission_v2.png',out/'Figures/fig1_mission_v2.png')
    text=(source/'main.tex').read_text()
    text=text.replace('\\usepackage{tabularx}','\\usepackage{tabularx}\n\\usepackage{microtype}\n\\setlength{\\emergencystretch}{2em}')
    text=text.replace('\\end{frontmatter}','\\end{frontmatter}\n\\normalsize')
    abstract=r'''Unmanned aerial vehicles must select among heterogeneous access networks while maintaining time-sensitive telemetry and image delivery. This study develops a task-conditioned predictive vertical-handover framework combining stacked LSTM forecasting, learned attention-based attribute weights, TOPSIS ranking, and persistent handover confirmation. A risk-aware extension adapts the score margin and penalizes uncertain candidates using residual variability. A three-stage mission comprises departure through a 5G NR region, slow imaging near a Wi-Fi station, and LTE-supported return. The simulator uses actual NR, LTE and Wi-Fi protocol stacks, a shared upstream payload process, packet-level deadlines and explicit application-layer service migration. An independent service-model optimizer evaluates unrestricted network sequences and switching costs. Three development missions support two service-reference transitions, providing a controlled setting for paired packet-level evaluation and prediction ablations.'''
    text=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',text,flags=re.S)
    intro_start=text.index('To address these challenges, this paper proposes LAAVHA')
    intro_end=text.index('Simulation results across 250 extended',intro_start)
    text=text[:intro_start]+'''To address these challenges, LAAVHA combines multihorizon LSTM forecasting, task-conditioned attention weights, fused-state TOPSIS and persistent handover confirmation. The prediction stage anticipates changes in candidate service; learned weights respond to network state, speed, altitude and current application demand. A causal forecast-error check reduces reliance on uncertain predictions. A separate recovery path responds to serving-link failure. ALERA extends the score rule with a residual-variability penalty and a margin adapted to detrended SINR increments. The evaluation measures whether these mechanisms preserve timely telemetry and image delivery while avoiding transient intermediate migrations.\n\n'''+text[intro_end:]
    start=text.index('Simulation results across 250 extended')
    end=text.index('\\section{Network Scenario',start)
    text=text[:start]+'''The evaluation connects predictive selection to task-level service outcomes. An independent service-reference optimizer compares unrestricted network sequences and explicit migration costs, while paired physical integration missions measure telemetry deadline delivery, image goodput and interruption. This evaluation distinguishes timely, useful migration from a low switch count obtained by retaining an unsuitable link.\n\n'''+text[end:]
    start=text.index('\\section{Network Scenario')
    end=text.index('\\section*{CRediT',start)
    pilot=ROOT/'outputs/physical_pilot/comparison.csv'
    evidence='Pilot results are still being collected. No aggregate test-set claim is made.'
    table=''
    if pilot.exists():
        d=pd.read_csv(pilot);groups=d.groupby('algorithm')
        lines=[]
        for name,g in groups:
            name={'ewma':'moving-average','strongest-signal':'strongest-SINR'}.get(name,name)
            lines.append(f"{name.replace('_','-')} & {len(g)} & {g.raw_handover_count.mean():.2f} & {100*g.telemetry_on_time_ratio.mean():.2f} & {100*g.video_on_time_ratio.mean():.2f} \\\\")
        table='''\n\\begin{table}[ht]\n\\centering\\small\n\\caption{Physical integration pilots. These missions are development evidence, not the held-out benchmark. Delivery denotes the fraction of generated payload packets received by their deadlines.}\n\\begin{tabular}{lrrrr}\\hline\nMethod & Missions & Switches & Telemetry (\\%) & Video (\\%) \\\\ \\hline\n'''+ '\n'.join(lines)+'''\n\\hline\\end{tabular}\n\\end{table}\n'''
        evidence=f'Physical integration pilots cover {d.seed.nunique()} mission seeds. Table~\\ref{{tab:pilot}} reports their descriptive means. These seeds were used during development; they provide no held-out generalization estimate.'
        la=d[d.algorithm.eq('laavha')]
        if len(la):
            counts=', '.join(str(int(v)) for v in la.sort_values('seed').raw_handover_count)
            evidence+=f' LAAVHA records raw switch counts of {counts}, with mean telemetry and video deadline delivery of {100*la.telemetry_on_time_ratio.mean():.2f}\\% and {100*la.video_on_time_ratio.mean():.2f}\\%, respectively.'
        if len(d) and d.raw_handover_count.eq(2).all():
            evidence+=' All evaluated methods achieve two migrations in these missions; their delivered service differs with migration timing.'
        table=table.replace('\\begin{tabular}', '\\label{tab:pilot}\n\\begin{tabular}',1)
    reference_table=''
    reference_rows=[]
    for seed in [100,108,119]:
        f=ROOT/f'outputs/height75_calibration/ns3_fixed-nr_seed{seed}.summary.json'
        if not f.exists():continue
        ref=json.loads(f.read_text())['reference_model']
        reference_rows.append(f'{seed} & '+ ' & '.join(f'{ref[k]["objective"]:.4f}' for k in ['0','1','2','None'])+f' & {ref["None"]["switches"]} '+r'\\')
    if reference_rows:
        reference_table=r'''\begin{table}[ht]\centering\small
\caption{Independent fresh-cohort service reference on fixed-NR calibration observations. The objective includes modeled interruption and switching cost. Columns 0--2 impose at most that many switches; the unrestricted solution has no count limit.}
\label{tab:reference}
\begin{tabular}{rrrrrr}\hline
Seed & 0 & 1 & 2 & Unrestricted & Count \\ \hline
'''+ '\n'.join(reference_rows)+r'''
\hline\end{tabular}\end{table}
The two-switch optimum exceeds every zero- or one-switch solution in these calibration missions. Allowing additional switches does not improve the objective. The selected sequence is NR--Wi-Fi--LTE. This result follows from the measured candidate service estimates and the declared objective.
'''
    prediction_table=''
    packet_reference_table=''
    packet_reference_rows=[]
    for label,folder in [('One-switch reference','physical_reference_one'),('Two-switch reference','physical_reference_two')]:
        f=ROOT/f'outputs/{folder}/ns3_offline-reference_seed100.summary.json'
        if f.exists():
            r=json.loads(f.read_text())
            packet_reference_rows.append(f'{label} & {r["raw_handover_count"]} & {100*r["telemetry_on_time_ratio"]:.2f} & {100*r["video_on_time_ratio"]:.2f} & {r["video_on_time_mbps"]:.3f} '+r'\\')
    if packet_reference_rows:
        packet_reference_table=r'''\begin{table}[ht]\centering\small
\caption{Packet-level replay of schedules obtained from fixed-NR calibration, seed 100. Both schedules are offline references with access to future candidate estimates.}
\label{tab:packet_reference}
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrr}\hline
Schedule & Switches & Telemetry (\%) & Video (\%) & Goodput (Mbps) \\ \hline
'''+ '\n'.join(packet_reference_rows)+r'''
\hline\end{tabular}\end{table}
The two-switch reference supplies the imaging stage through Wi-Fi and preserves substantially more deadline-qualified service in this replay.
'''
    model_json=ROOT/'artifacts/physical_model.json'
    if model_json.exists():
        meta=json.loads(model_json.read_text())
        prediction_table=r'''\begin{table}[ht]\centering\small
\caption{Prediction validation on two complete missions, seeds 100 and 101. MSE is normalized with training-mission attribute scales.}
\label{tab:prediction}
\begin{tabular}{rrrr}\hline
Horizon (s) & LSTM & Persistence & Linear trend \\ \hline
'''+ '\n'.join(f'{h:.1f} & '+ ' & '.join(f'{meta["validation_mse"][name][i]:.6f}' for name in ['lstm','persistence','linear'])+r' \\' for i,h in enumerate([.1,.3,.5]))+r'''
\hline\end{tabular}\end{table}
'''
    section=r'''
\section{Mission Scenario and Measurement Model}\label{sec:scenario}
The mission occupies a $2000\times2000$ m region. The NR gNB, LTE eNB and Wi-Fi access point are located at $(1500,1000,30)$, $(700,1000,30)$ and $(1000,1000,10)$ m, respectively. The UAV starts near $(1600,1000,100)$ m and flies west. Its nominal horizontal speed is 30 m/s during departure, 5 m/s near the imaging station, and 25 m/s during return, with one-second continuous transitions. Position and altitude perturbations are sampled once per mission. Figure~\ref{fig:network_coverage} is generated from the executable mission configuration.
\begin{figure}[ht]\centering
\includegraphics[width=\textwidth]{Figures/fig1_mission_v2.png}
\caption{Three-stage mission, geometric obstruction and nominal coverage scales. Coverage circles guide layout and do not impose receiver availability or switching times.}
\label{fig:network_coverage}\end{figure}
The application generates 64 kbps telemetry throughout the mission, with a 50 ms deadline. Preview traffic is 2 Mbps; within the geographic imaging interval $950\leq x\leq1000$ m, image traffic is 8 Mbps. Video/image packets have a 200 ms deadline. Every policy receives the same current task requirement. All traffic is upstream to a common server, and payload generation is independent of the selected network.

The physical platform comprises ns-3.45, 5G-LENA v4.1, LTE/EPC and 802.11n Wi-Fi. The engineering propagation model uses log-distance exponents 2.8, 3.1 and 3.0 for NR, LTE and Wi-Fi, with respective 1 m reference losses of 43.3, 38 and 40 dB. This is a declared engineering air-link model rather than a validated TR38.901 UAV channel. A building spanning $x=1100$--1150 m, $y=900$--1100 m and $z=0$--85 m introduces an 18 dB loss when a propagation ray intersects it. This loss acts on actual radio power. Its value is subject to sensitivity evaluation. LTE has a declared 6 Mbps backhaul allocation. The same physical assumptions apply to every policy.

Three co-moving radio-endpoint nodes represent one logical UAV. The application coordinator sends each payload packet through one endpoint only. A service migration changes that endpoint and introduces a modeled 100 ms application interruption; packets generated during that interval are counted as interruption losses. The implementation does not execute a cross-RAT attach procedure and does not interpret the interruption parameter as measured protocol latency. Interfaces are connected and probed during a two-second warmup; the 50 s mission begins with verified NR service.

Candidate observations comprise receiver SINR, received reference power/RSSI, probe delay, a PHY-based available-capacity estimate, and probe deadline loss. These estimates are distinct from payload goodput. Probes use shared generation intervals and their own packet cohorts. A cohort is evaluated only after its deadline; in-flight packets are not counted as lost. A missing delay is explicitly flagged and mapped to a conservative representation. Actual telemetry and image outcomes are computed from unique payload identifiers and application generation/receive timestamps, followed by a one-second drain interval.

\section{Task-Conditioned LAAVHA and ALERA}\label{sec:laavha}
Each candidate contributes ten historical states separated by 0.1 s. Two LSTM layers, with 128 and 64 hidden units, forecast the five indicators at horizons 0.1, 0.3 and 0.5 s. The same physical clipping applies before training and inference: SINR is bounded to $[-50,80]$ dB, received power to $[-180,-10]$ dBm, delay to $[0,1000]$ ms, estimated capacity to $[0,200]$ Mbps and loss to $[0,1]$. Below-floor native reference-power values enter as the conservative lower bound. Training means and standard deviations are fitted on whole training missions and stored with the checkpoint. A causal forecast-error check guards inference. The score-fusion stage uses the 0.3 s prediction and falls back toward current measurements when recent forecast errors are large.

The weighting branch embeds current network states into 16-dimensional vectors, applies single-head self-attention, pools across candidates and concatenates normalized speed, altitude and current traffic demand. A trained projection produces five attribute weights:
\begin{equation}w_j=0.04+0.8\,\mathrm{softmax}(z)_j.\end{equation}
The floor prevents an attribute from being completely discarded. The training loss combines normalized multihorizon prediction MSE, candidate-ranking supervision from a fixed external service objective, and weight regularization. Both prediction and weighting branches receive gradients. Validation selects checkpoints using prediction and ranking loss; adjacent windows from one mission are never split across training and validation.
\begin{equation}
\mathcal L=\mathcal L_{\mathrm{pred}}-\frac1N\sum_{n,i}p_{ni}\log q_{ni}
+0.1\frac1{5N}\sum_{n,j}(w_{nj}-0.2)^2,
\end{equation}
where $p_{ni}$ is the softmax distribution of external service values at temperature 0.1 and $q_{ni}$ is the softmax distribution of weighted TOPSIS scores at the same temperature. Training uses complete missions 0--7; validation uses missions 100 and 101. Adam uses learning rate 0.001 and batch size 128 for 35 epochs, with validation checkpoint selection.
% PREDICTION_EVIDENCE

Fixed engineering transforms map the five indicators to benefit features. For current video demand $d$, the benefit features are
\begin{equation}
f(S,d)=\operatorname{clip}_{[0,1]}\left[
\frac{\mathrm{SINR}+10}{40},\frac{P+120}{70},
e^{-D/50},\min(C/d,1),1-L\right].
\end{equation}
Here $P$ is received reference power or RSSI in dBm, $D$ is probe delay in ms, $C$ is estimated capacity in Mbps, and $L$ is probe deadline loss. The nominal current-state coefficient is $\alpha=0.6$. If $e_t$ is the mean absolute feature error of the previous one-step forecast, confidence is $c_t=e^{-e_t/0.15}$ and the effective current-state coefficient is $a_t=1-(1-\alpha)c_t$. Thus low confidence shifts the fused features toward observations. Weighted TOPSIS computes candidate closeness from $a_t f(S_t,d_t)+(1-a_t)f(\hat S_{t+0.3},d_t)$. Normal migration requires a score advantage exceeding 0.03 for three consecutive decisions.

All compared policies share the same declared availability guard. A candidate must show recent service capacity of at least 0.1 Mbps, delay within 200 ms and loss below 0.5. Normal predictive migration additionally checks whether the 0.3 s and 0.5 s forecast rankings agree on a persistent destination. Such a destination must already be usable and better than the serving network; otherwise the policy defers a potentially short-lived intermediate migration. The same check is applied to simple predictive controls. When the serving link fails and another is usable, a two-step recovery rule overrides normal score hysteresis and predictive deferral. When all candidates are unavailable the policy retains its current interface and records outage. No policy receives a desired network order, a route-specific switching time or a handover-count limit.

ALERA subtracts a risk term based on recent score increments and adjusts the margin using detrended SINR increments. This distinguishes stochastic variation from a monotonic degradation trend. The implementation retains separate no-prediction and no-attention variants. Strong controls include task-weighted TOPSIS with the same guards and hysteresis, five-sample moving-average and linear prediction controls, strongest-SINR selection, and adapted MADM alternatives. The task-aware control uses weights (0.10,0.05,0.25,0.30,0.30) for preview and (0.05,0.05,0.15,0.45,0.30) for imaging, in the declared attribute order. This provides a direct test of whether learned weights add value. The moving-average control retains the historical CLI identifier \texttt{ewma}; its averaging window has uniform weights.
\begin{align}
\widetilde C_i(t)&=C_i(t)-0.5\operatorname{std}\{\Delta C_i\},\\
\Delta_{\mathrm{ALERA}}(t)&=0.03+
\min\left(0.05,\,0.005\operatorname{std}\{\Delta\mathrm{SINR}_{\mathrm{serving}}\}\right).
\end{align}
Both standard deviations use increments within the five most recent samples; the score history stores values before risk correction. A linear decline therefore contributes little residual variability. ALERA retains three-step normal confirmation and the shared two-step failure recovery.

\begin{algorithm}[ht]
\caption{Causal mission-conditioned LAAVHA selection}
\begin{algorithmic}[1]
\Require Historical candidate observations, current task demand and mobility, serving interface, confirmation state
\State Clip observations and update the ten-sample history
\State Forecast 0.1/0.3/0.5 s states and generate trained task-conditioned weights
\State Estimate confidence using the preceding one-step forecast error
\State Fuse current and 0.3 s benefit features; compute weighted TOPSIS scores
\State Apply ALERA residual correction when that variant is enabled
\State Determine usable candidates from recent capacity, delay and loss
\If{no candidate is usable}
  \State Keep serving interface and record unavailable service
\ElsIf{serving interface is unusable}
  \State Confirm a usable alternative for two decisions, then migrate
\Else
  \State Check agreement of 0.3/0.5 s forecast destinations
  \State Confirm a persistent usable score advantage for three decisions
  \State Migrate when confirmation and interruption constraints permit
\EndIf
\end{algorithmic}
\end{algorithm}

\section{Independent Reference and Validation}\label{sec:sim}
The offline reference uses an external task objective rather than TOPSIS closeness or learned weights. In its declared fresh-cohort service model, telemetry consumes capacity first, remaining capacity serves video, and cohorts missing their deadline yield no service. Telemetry satisfaction has weight four and video satisfaction weight one; an explicit switch cost is subtracted. A dynamic program tracks the serving network, interruption state and optional switch-count budget. It optimizes arbitrary network orders and counts. It is checked against exhaustive enumeration on short sequences.

The external objective is
\begin{equation}
J=\sum_t \bigl(4s_{\mathrm{telemetry},t}+s_{\mathrm{video},t}\bigr)
(1-\ell_t/\Delta t)\Delta t-0.02H,
\end{equation}
where satisfaction values follow priority capacity allocation and the respective deadlines, $\ell_t$ is the service time lost to migration in the slot, $\Delta t=0.1$ s and $H$ is the raw switch count. The reference is exact for this fresh-cohort service model. Physical packet queues and policy-dependent observations are evaluated separately by ns-3 replay.
% REFERENCE_EVIDENCE
Sensitivity evaluates switch costs 0.005/0.02/0.05 and interruption durations 0/0.05/0.1/0.2 s. Stress missions allow different reference counts, including an archived 85 m roof configuration whose coverage gap requires an intermediate LTE migration.

% PILOT_EVIDENCE
Primary measured outcomes are telemetry deadline delivery, image deadline goodput, payload delay percentiles, service-interruption losses and raw application migration count. An additional zero-delivery-cohort measure counts generation windows in which no payload packet subsequently arrives by its deadline. Repeated-seed summaries use missions as independent units. The integration comparison includes shared-guard task TOPSIS, simple prediction controls and component ablations.

\section{Conclusion}\label{sec:conclusion}
Task-conditioned LAAVHA connects predictive network selection to telemetry deadlines and image demand. The three-stage mission supports an independently evaluated two-transition service reference, while causal confidence checks, persistent destination selection and failure recovery govern online migration. Paired integration missions and component ablations expose the relationship between raw switching count and delivered payload. Further evaluation will quantify performance across held-out missions, background traffic and broader geometries.

'''
    section=section.replace('$z=0$--85 m',f'$z=0$--{CONFIG["building_bounds_m"][2][1]:g} m')
    section=section.replace('% REFERENCE_EVIDENCE',reference_table+'\n'+packet_reference_table).replace('% PREDICTION_EVIDENCE',prediction_table)
    timeline=ROOT/'figures/physical_timeline_seed100.png'
    extra=''
    if timeline.exists():
        shutil.copy2(timeline,out/'Figures'/timeline.name)
        extra=r'''\begin{figure}[ht]\centering
\includegraphics[width=\textwidth]{Figures/physical_timeline_seed100.png}
\caption{Physical pilot observations, selected interfaces and deadline-qualified video goodput for seed 100. Capacity estimates are used for decisions; the bottom panel is computed from received payload packets. Small vertical offsets distinguish coincident interface sequences.}
\label{fig:physical_timeline}\end{figure}'''
    section=section.replace('% PILOT_EVIDENCE',evidence+'\n'+table+'\n'+extra)
    text=text[:start]+section+text[end:]
    (out/'main.tex').write_text(text)
    proc=subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','main.tex'],cwd=out,capture_output=True,text=True)
    (out/'build.log').write_text(proc.stdout+proc.stderr)
    if proc.returncode:raise RuntimeError('Manuscript compile failed; inspect manuscript_revision/build.log')
    print(out/'main.pdf')


if __name__=='__main__':main()
