"""Evaluate saved forecasts against saved physical observations; run no simulator.

MSE uses checkpoint training scales and the same 10-step history/targets as
training. All candidate observations are included, including service failures.
Metrics describe each policy's recorded environment, not packet-optimal choices.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from mission import sanitize
from model import load_model, context_tensor


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path)
    ap.add_argument('--algorithm', default='laavha')
    args = ap.parse_args()
    directory = args.directory.resolve()
    model, _ = load_model(directory/'frozen_inputs/checkpoint.pt')
    torch.set_num_threads(1)
    manifest = json.loads((directory/'manifest.json').read_text())
    rows = []
    for seed in manifest['seeds']:
        with np.load(directory/f'ns3_{args.algorithm}_seed{seed}.trace.npz') as trace:
            metrics = sanitize(trace['metrics'])
            indices = np.arange(9, len(metrics)-5, 2)
            histories = np.stack([metrics[i-9:i+1].transpose(1, 0, 2) for i in indices])
            contexts = torch.stack([context_tensor(trace['speed'][i], trace['position'][i, 2], trace['demand'][i]) for i in indices])
            targets = np.stack([metrics[i+np.array([1, 3, 5])].transpose(1, 0, 2) for i in indices])
        with torch.no_grad():
            prediction, _ = model(torch.tensor(histories, dtype=torch.float32), contexts)
        persistence = np.repeat(histories[:, :, -1:, :], 3, axis=2)
        slope = (histories[:, :, -1] - histories[:, :, -3]) / 2
        linear = histories[:, :, -1:, :] + slope[:, :, None, :] * np.array([1, 3, 5])[None, None, :, None]
        scale = model.scale.detach().numpy()
        for name, values in [('lstm', prediction.numpy()), ('persistence', persistence), ('linear', linear)]:
            mse = np.mean(((values-targets)/scale)**2, axis=(0, 1, 3))
            for horizon, value in zip([.1, .3, .5], mse):
                rows.append(dict(seed=seed, predictor=name, horizon_s=horizon,
                                 samples=len(indices), normalized_mse=float(value)))
    data = pd.DataFrame(rows)
    data.to_csv(directory/'prediction_diagnostics.csv', index=False)
    summary = data.groupby(['predictor', 'horizon_s']).normalized_mse.agg(['mean', 'std'])
    summary.to_csv(directory/'prediction_diagnostics_summary.csv')
    print(summary.to_string())


if __name__ == '__main__':
    main()
