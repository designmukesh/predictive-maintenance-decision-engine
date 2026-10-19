"""Input bridges: generate decision-engine inputs from projects #1 and #2.

- RUL backtest data: out-of-sample RUL predictions for project #2's 20
  validation engines (full trajectories, true RUL known). The model is trained
  on the other 80 engines — never on the engines being decided on.
- Hydraulic fault predictions: quick RF retrain on project #1 data with a
  held-out split, returning predicted states + probabilities per cycle.

Both reuse the tested src/ modules of the earlier projects; this project
adds the decision layer, not new ML.
"""
import sys
from pathlib import Path

import numpy as np

P1 = Path(__file__).resolve().parent.parent.parent / "01-hydraulic-condition-monitoring"
P2 = Path(__file__).resolve().parent.parent.parent / "02-nasa-turbofan-rul"


def _load_p2_src():
    """Load project #2's src/ as package `p2src` (avoids clashing with our src)."""
    import importlib.util

    if "p2src" in sys.modules:
        return sys.modules["p2src"]
    pkg_path = P2 / "src"
    spec = importlib.util.spec_from_file_location(
        "p2src", pkg_path / "__init__.py",
        submodule_search_locations=[str(pkg_path)])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["p2src"] = pkg
    spec.loader.exec_module(pkg)
    return pkg


_p2src = _load_p2_src()
from p2src.data import load_subset as p2_load  # noqa: E402
from p2src.features import window_features as p2_windows  # noqa: E402
from p2src.models import get_models as p2_models  # noqa: E402


def load_rul_backtest(data_dir=None, seed=42):
    """Out-of-sample RUL predictions for project #2's 20 validation engines.

    Returns:
      engines: dict engine_id -> {"true": np.array, "pred": np.array}
               aligned per cycle (one value per operating cycle)
      residuals: np.array of (pred - true) on validation windows
    """
    data_dir = data_dir or (P2 / "data")
    train, _, _ = p2_load("FD001", data_dir)
    Xw, yw, units = p2_windows(train)
    rng = np.random.default_rng(seed)
    engs = train.unit.unique()
    rng.shuffle(engs)
    n_tr = int(0.8 * len(engs))
    tr, va = set(engs[:n_tr]), set(engs[n_tr:])
    tr_m = np.isin(units, list(tr))
    va_m = np.isin(units, list(va))

    model = p2_models()["HistGradientBoosting"]
    model.fit(Xw[tr_m], yw[tr_m])
    pred_va = model.predict(Xw[va_m])
    residuals = pred_va - yw[va_m]

    # per-engine trajectories: window i of engine u covers cycles; the label
    # is the RUL at the window's end. Rebuild per-cycle series from windows:
    # pred at cycle c = prediction of window ending at c (cycles 30..end).
    engines = {}
    for u in sorted(va):
        d = train[train.unit == u].sort_values("cycle").reset_index(drop=True)
        life = int(d.cycle.max())
        true_rul = np.array([min(125, life - c) for c in d.cycle])
        mask = units[va_m] == u
        pw = pred_va[mask]  # one per window, windows end at cycles 30..life
        pred_rul = np.full(life, np.nan)
        pred_rul[29:] = pw  # window ending at cycle c -> index c-1
        # backfill early cycles (no window yet): hold first prediction
        pred_rul[:29] = pw[0]
        engines[u] = {"true": true_rul, "pred": pred_rul, "life": life}
    return engines, residuals


def load_hydraulic_predictions(data_dir=None, seed=42, test_size=0.2):
    """Quick RF retrain on project #1 data; held-out predicted states.

    Returns DataFrame with one row per held-out cycle:
    component, true_state, pred_state, max_probability.
    """
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    import importlib.util
    import types

    if "p1src.data" not in sys.modules:
        # project #1's src/ has no __init__.py: register a namespace-style
        # parent package and load data.py into it by path.
        parent = types.ModuleType("p1src")
        parent.__path__ = [str(P1 / "src")]
        sys.modules["p1src"] = parent
        spec = importlib.util.spec_from_file_location(
            "p1src.data", P1 / "src" / "data.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["p1src.data"] = mod
        spec.loader.exec_module(mod)
    from p1src.data import (  # noqa: E402
        TARGET_LABELS, TARGETS, build_feature_frame, load_profile,
    )

    prof = load_profile()
    X = build_feature_frame(verbose=False)
    assert len(X) == len(prof) == 2205
    out = []
    for target in TARGETS:
        # numeric codes -> human labels via project #1's TARGET_LABELS
        labels = np.array([TARGET_LABELS[target][int(v)]
                           for v in prof[target].values])
        Xtr, Xte, ytr, yte = train_test_split(
            X.values, labels, test_size=test_size, random_state=seed,
            stratify=labels)
        clf = RandomForestClassifier(n_estimators=200, n_jobs=-1,
                                     random_state=seed)
        clf.fit(Xtr, ytr)
        proba = clf.predict_proba(Xte)
        pred = clf.classes_[proba.argmax(axis=1)]
        conf = proba.max(axis=1)
        for t, p, c in zip(yte, pred, conf):
            out.append({"component": target, "true_state": t,
                        "pred_state": p, "confidence": float(c)})
    return pd.DataFrame(out)
