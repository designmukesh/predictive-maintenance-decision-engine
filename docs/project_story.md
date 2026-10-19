# Project Story — why this project exists

Projects #1 and #2 were about *prediction*: what's the machine's condition, how
much life is left. Every time I presented that kind of work, the same question
came back from the operations side: **"So what do we do on Tuesday?"**

A prediction is not a decision. A planner holding "RUL = 40 cycles" still has to
answer: intervene now or wait? What does waiting cost if we're wrong? What does
acting early waste? Most "AI for maintenance" decks stop at the ROC curve and
never touch these questions — which is why pilots stall at the handoff between
the data team and the people with wrenches.

This project is the handoff, engineered:

1. **Costs first.** Before any threshold, write down what each mistake costs.
   Normalize, label the assumptions, and let the economics derive the rule
   (act when failure risk exceeds 1/k) instead of inheriting folklore like
   "replace at RUL < 30".
2. **Honest uncertainty.** The decision needs P(failure), not a point estimate.
   Take it from observed errors — 3,524 of them — not from a Gaussian you
   wished for.
3. **Spend simulated money.** Backtest policies the way you'd backtest a trading
   strategy: same engines, same predictions, different rules, exact bills.
   Let run-to-failure and fixed-interval lose on the record.
4. **Say what the model can't.** The L-shaped cost curve, the k-insensitive
   optimum, the unmonetized wasted life — the interesting findings were the ones
   that *complicated* the story, and they're all in the notebooks.

The deliverable isn't the 80% saving — it's the method. Any planner's costs plug
straight in, and the first thing the framework tells them might be that their
fixed schedule was already fine. That's a successful project too.
