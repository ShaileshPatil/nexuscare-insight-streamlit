# NexusCare Insight — Streamlit Replica

A local Streamlit rebuild of the NexusCare Insight Lovable UI
(https://nexuscare-insight.lovable.app/), built to remove the dependency
on Humana's network being able to reach the `*.lovable.app` domain during
the live panel presentation.

Data (`demo_export.json`) and all visible text/values are copied verbatim
from the Lovable app's own export, with **one intentional exception**:
Linda K.'s Scheduling node is shown as "Skipped" (grey icon/chip) instead
of "Done", with reworded decision text explaining that no new scheduling
action was needed because her surgeon follow-up was already confirmed in
the discharge summary. This fix is applied **only in this Streamlit
rebuild** — the live Lovable app / its GitHub repo were not touched.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501 — fully offline after the pip install,
no network dependency at presentation time.

## What matches the live app
- All three patient cases (Margaret T., James R., Linda K.) with exact
  risk scores, tiers, brief text, and outreach messages
- Discharge Worklist sidebar with risk-sorted cases
- Agent Reasoning Trace (5 nodes, exact decisions/latencies)
- Coordinator Brief: risk factors, extracted facts (with red-flag styling),
  editable outreach message, validation checks, critic verdict
- Sources & Citations panel, Proposed Follow-Up, Coordinator Actions
  (Approve & Send / Escalate — simulated, same as the live demo)

## Known differences (Streamlit rendering constraints)
- No entrance animations or the live "replaying trace" loading sequence
  (all trace nodes render as already-complete, matching the live app's
  end state)
- Colors are hex approximations of the live app's OKLCH CSS variables —
  visually very close but not pixel-identical
- Citations use Streamlit's native expander instead of a custom accordion
