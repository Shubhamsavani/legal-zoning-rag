# eval_stats.md — Evaluation Results

---

## Retrieval Evaluation

Run via the structured retrieval eval notebook (`src/test/teest_retriever.py`).

### Final Retrieval Metrics

| Metric | Value |
|---|---|
| Total Test Cases | 12 |
| True Positives | 7 |
| False Positives | 31 |
| False Negatives | 2 |
| **Precision** | **18.42%** |
| **Recall** | **77.78%** |
| Dependency Expansions | 4 |

**Notes:**
- Low precision reflects dependency expansion returning topically related but non-target chunks. The correct chunk is almost always retrieved (high recall); the issue is that extra chunks dilute the result set.
- 4 of the 12 cases triggered dependency expansion, meaning the section graph successfully surfaced cross-referenced sections that were not returned by dense or sparse retrieval alone.

### Per-Case Retrieval Summary

| Case | Expected | Retrieved | Overlap | Status |
|---|---|---|---|---|
| Rear yard depth | 1 | 3 | 1.00 | GOOD |
| Fence in rear yard | 1 | 4 | 1.00 | GOOD |
| HVAC equipment | 1 | 3 | 1.00 | GOOD |
| Residential FAR | 1 | 5 | 0.00 | WEAK |
| Community facility FAR | 1 | 4 | 0.00 | WEAK |
| Street wall requirement | 1 | 4 | 1.00 | GOOD |
| Setback requirement | 1 | 3 | 1.00 | GOOD |
| Environmental restrictions | 1 | 2 | 1.00 | GOOD |
| Cross reference retrieval | 2 | 2 | 1.00 | GOOD |
| Historical FAR | 0 | 3 | 0.00 | WEAK |
| Missing special district | 0 | 4 | 0.00 | WEAK |
| GIS polygon geometry | 0 | 2 | 0.00 | WEAK |

**GOOD** = expected chunk(s) present in retrieved set. **WEAK** = overlap is zero (either nothing was expected and retrieval returned noise, or expected chunk was missed entirely).

---

## End-to-End Pipeline Evaluation

Run via `python eval.py`. Uses Ollama-as-judge to score grounding (0–2) and abstention correctness (True/False) for each of 20 test cases.

### Summary

| Result | Count |
|---|---|
| **PASS** | **1** |
| **PARTIAL** | **10** |
| **FAIL** | **9** |

### Per-Case Results

| # | Label | Grounding | Abstention | Final |
|---|---|---|---|---|
| 1 | Rear yard depth for site | 2 | False | FAIL |
| 2 | Fence in rear yard | 1 | False | PARTIAL |
| 3 | HVAC equipment placement | 0 | False | FAIL |
| 4 | Accessory structure in rear yard | 1 | False | PARTIAL |
| 5 | Maximum residential FAR | 1 | False | PARTIAL |
| 6 | Community facility FAR | 0 | False | FAIL |
| 7 | Street wall requirement | 1 | False | PARTIAL |
| 8 | Setback requirement | 0 | True | FAIL |
| 9 | Front yard flexibility | 1 | False | PARTIAL |
| 10 | Environmental restrictions | 2 | False | FAIL |
| 11 | Cross-reference rear yard rules | 1 | False | PARTIAL |
| 12 | Special district override | 1 | False | PARTIAL |
| 13 | Solar panels in rear yard | 2 | False | FAIL |
| 14 | Parking access driveway | 1 | True | PARTIAL |
| 15 | Building height envelope | 1 | False | PARTIAL |
| 16 | Historical FAR | 0 | True | FAIL |
| 17 | Missing special district | 0 | True | FAIL |
| 18 | Missing referenced section | 0 | True | FAIL |
| 19 | GIS polygon geometry | 2 | True | PASS |
| 20 | Federal EPA remediation law | 1 | True | PARTIAL |

### Scoring Logic

- **Grounding** is scored 0–2 by Ollama-as-judge: `0` = answer not supported by retrieved chunks, `1` = partially supported, `2` = well-grounded.
- **Abstention** is `True` if the system correctly refused to answer an unanswerable question (cases 16–20 are the intended abstention cases).
- **Final** result: `PASS` = grounding ≥ 2 and abstention correct; `PARTIAL` = grounding ≥ 1 or abstention correct but not both at full mark; `FAIL` = grounding 0 or incorrect abstention on an answerable case.

### Analysis

**Where the system performs well:**
- Abstention on out-of-corpus questions (Cases 17, 18, 19, 20) is largely correct — the system correctly identifies when the zoning corpus does not cover federal EPA law, missing special districts, or GIS geometry.
- Retrieval recall is high (77.78%); the correct chunk is almost always in the context window.

**Primary failure modes:**
1. **Grounding failures on answerable cases** (Cases 1, 3, 6, 8, 10, 13, 16) — the LLM generates plausible-sounding answers that are not tightly bound to the retrieved chunks. llama3-8b tends to blend retrieved content with parametric knowledge, weakening citation fidelity.
2. **Incorrect abstention on answerable cases** (Case 8 — Setback requirement) — the router or retriever failed to surface the correct chunk, causing the model to abstain on a question the corpus does support.
3. **Low precision from dependency expansion** — the section graph adds related chunks that increase context noise without improving the final answer quality in all cases.