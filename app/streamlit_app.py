"""Predictive Maintenance Decision Engine — interactive Streamlit demo.

What it does:
  1. Lets you set the cost assumption k (= unplanned / planned) and the
     decision threshold T, then backtests three policies live on the 20
     validation engines from project #2 (out-of-sample RUL predictions).
  2. Shows a per-engine timeline: predicted vs true RUL and where the
     policy would have intervened.
  3. Explores the hydraulic fault-state decision table (project #1 outputs).

Run: streamlit run app/streamlit_app.py  (from the repo root)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import pandas as pd
import streamlit as st

from src.costs import MaintenanceCosts
from src.fault_decisions import DECISION_TABLE, action_cost, decide
from src.policies import (simulate_fixed_interval, simulate_predictive,
                          simulate_run_to_failure, summarize)

st.set_page_config(page_title="Maintenance Decision Engine",
                   page_icon="🔧", layout="wide")
st.title("🔧 Predictive Maintenance — Decision Engine")
st.caption("Project #3 · turns RUL predictions (project #2) and fault states "
           "(project #1) into maintenance decisions under an explicit cost model. "
           "All costs are assumption-labeled, normalized to planned = 1.0.")


@st.cache_data(show_spinner="Loading validation engines (trains RUL model)…")
def load_engines():
    from src.inputs import load_rul_backtest
    return load_rul_backtest()


engines, residuals = load_engines()
eng_list = [engines[u] for u in sorted(engines)]

# ---------- sidebar: the two numbers that matter ----------
st.sidebar.header("Policy parameters")
k = st.sidebar.slider("Unplanned / planned cost ratio (k)", 2.0, 10.0, 5.0, 0.5)
T = st.sidebar.slider("Predictive threshold T (act when pred RUL ≤ T)",
                      0, 60, 20, 1)
N = st.sidebar.slider("Fixed-interval N (cycles)", 10, 150, 50, 5)
lead = st.sidebar.slider("Intervention lead time (cycles)", 0, 5, 1, 1)
costs = MaintenanceCosts(unplanned_multiplier=k, lead_time=lead)

st.sidebar.markdown(
    f"**Decision rule:** act when P(fail within horizon) × {k:.1f} > 1.0, "
    f"i.e. failure risk above **{1/k:.0%}**.")

# ---------- policy comparison ----------
st.header("1 · Policy backtest (20 validation engines, out-of-sample)")
rtf = summarize([simulate_run_to_failure(e["life"], costs) for e in eng_list])
fix = summarize([simulate_fixed_interval(e["life"], N, costs) for e in eng_list])
pre = summarize([simulate_predictive(e["true"], e["pred"], float(T), costs)
                 for e in eng_list])

comp = pd.DataFrame([
    {"policy": "Run-to-failure", **{kk: rtf[kk] for kk in
     ["cost_per_engine", "unplanned_rate", "mean_wasted_life"]}},
    {"policy": f"Fixed-interval (N={N})", **{kk: fix[kk] for kk in
     ["cost_per_engine", "unplanned_rate", "mean_wasted_life"]}},
    {"policy": f"Predictive (T={T})", **{kk: pre[kk] for kk in
     ["cost_per_engine", "unplanned_rate", "mean_wasted_life"]}},
]).set_index("policy")
comp.columns = ["cost / engine", "unplanned rate", "mean wasted life (cycles)"]
st.dataframe(comp.style.format("{:.2f}"), use_container_width=True)

saving = (1 - pre["cost_per_engine"] / rtf["cost_per_engine"]) * 100
st.success(f"At k={k:.1f}, the predictive policy (T={T}) costs "
           f"**{pre['cost_per_engine']:.2f}** per engine vs "
           f"**{rtf['cost_per_engine']:.2f}** for run-to-failure — "
           f"a **{saving:.0f}%** illustrative saving, with "
           f"{pre['unplanned_failures']}/{len(eng_list)} unplanned failures.")

st.bar_chart(comp[["cost / engine"]])

# ---------- per-engine timeline ----------
st.header("2 · Per-engine timeline")
u = st.selectbox("Engine", sorted(engines), index=0)
e = engines[u]
r = simulate_predictive(e["true"], e["pred"], float(T), costs)
cyc = np.arange(1, len(e["true"]) + 1)
tl = pd.DataFrame({"cycle": cyc, "true RUL": e["true"],
                   "predicted RUL": np.round(e["pred"], 1)}).set_index("cycle")
st.line_chart(tl)
if r["acted_at"] is not None:
    st.info(f"Policy intervenes at cycle **{r['acted_at']+1}** "
            f"(predicted RUL {e['pred'][r['acted_at']]:.1f} ≤ {T}); "
            f"true remaining then **{e['true'][r['acted_at']]:.0f}** cycles → "
            f"cost {r['cost']:.1f} (planned). Wasted healthy life: "
            f"{r['wasted_life']:.0f} cycles.")
else:
    st.warning(f"Policy never fires (T={T}) — engine runs to failure at cycle "
               f"{e['life']}, cost {r['cost']:.1f} (unplanned).")

# ---------- fault-state explorer ----------
st.header("3 · Fault-state decision table (hydraulic system)")
comp_sel = st.selectbox("Component",
                        sorted({c for c, _ in DECISION_TABLE}))
states = sorted({s for c, s in DECISION_TABLE if c == comp_sel})
state_sel = st.selectbox("Predicted state", states)
action, why = decide(comp_sel, state_sel)
st.markdown(f"**Action: `{action}`** — cost {action_cost(action, costs):.2f}")
st.caption(why)

with st.expander("Full decision table"):
    rows = [{"component": c, "predicted state": s, "action": a}
            for (c, s), (a, _) in sorted(DECISION_TABLE.items())]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
st.caption("Honesty notes: cost ratios are assumed parameters, not observed. "
           "Backtest uses 20 validation engines — a small sample; treat "
           "percentages as illustrative. Predictions are out-of-sample "
           "(model trained on the other 80 engines).")
