# Lab 19 validation — 5 November 2026

**Completed:** COST baseline and threshold probe, NVDA company run, three memos for each company, financial checks and app tests. **Pending:** personal and partner work, GitHub publication and Brightspace checkout.

The COST panel was recomputed from `../Lab18/results/COST_companyfacts.json`. Its SHA-256 was checked against the preserved source metadata before extraction. The new ratios match the official answer: 2.11, 1.75, 1.96, 1.64, 1.49; revenue CAGR is 7.51%; R&D remains absent. Buffett passes all three checks, Wood fails growth with unknown R&D, and Burry passes both checks.

The 5% skill configuration was run separately, with outputs saved in `results/probe_5pct/`. Wood's growth check changes to pass; R&D remains unknown. A test confirms that every underlying financial row is identical across configurations. The retained default remains 15%.

Nine panel tests passed:

- Recomputed COST known-answer comparison.
- Threshold probe with unchanged facts.
- Missing inputs and nonpositive revenue.
- Incomplete history and skipped fiscal years.
- Unrounded boundary comparisons.
- Missing cash-flow inputs take precedence over an observed failure.
- R&D fallback, annual filtering, latest-filing selection and instant liabilities.
- Nonpositive equity and missing liabilities.
- All saved COST memos pass; an unsupported percentage injected into each investor's memo is flagged; sign and percent distinctions are preserved.

Seven existing Lab18 checks also passed: its six synthetic extraction/audit tests and the COST known-answer test. The pre-existing JPM tests were not run because no JPM download or memo exists; that is separate Lab18 pending work.

Streamlit AppTest verified the upgraded app renders without exceptions or error messages, exposes three memo editors, shows the threshold-probe notice, and flags `987.654321%` when injected independently into each of the three editors. The health endpoint at localhost:8518 returned `ok` after the extension.

Both new skill manifests passed `quick_validate.py`, using cached PyYAML through the workspace uv environment. Relative links in `.agents/skills/` were created successfully.

Run the panel tests from the course root:

```bash
.venv/bin/python -m unittest discover -s "ColinSpensley/Project 2/Lab19" -p 'test_*.py' -v
```

Manual interpretation check: the COST Burry memo correctly distinguishes the latest-year liabilities test from the earlier ratio above the ceiling; Wood does not equate missing R&D with zero; Buffett does not infer a moat or fair stock price from the passing financial screens. The memos contain model judgments rather than code-assigned verdicts.

## NVIDIA company run

The user supplied the SEC contact header. The downloader retrieved NVIDIA's raw SEC company facts at `2026-11-05T22:10:15.682750+00:00` from `https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json`. The saved SHA-256 is `19ef503a5770f5660964b3c3aea6937579d9b359da344afe6a9adf59c63d26ff`. The raw response and source record are in `../Lab18/results/`; the panel verifies the digest, ticker and CIK before reading it.

Five fiscal periods end on 2022-01-30, 2023-01-29, 2024-01-28, 2025-01-26 and 2026-01-25. The engine uses the allowed revenue-tag fallback and PaymentsToAcquireProductiveAssets for capital spending. Per-value tags, periods, filing dates and accessions are printed in `results/NVDA_output.txt`.

Buffett passes all three checks. Wood passes revenue growth at 68.30% and latest R&D intensity at 8.57%. Burry fails cash flow >= income every year, with failures in FY2022, FY2024, FY2025 and FY2026; latest liabilities/equity passes at 0.31. No missing required inputs were replaced with estimates.

All three NVDA memos were written after the outputs were read and passed the shared numeric audit. Manual review confirms they distinguish R&D spending from R&D intensity, recognize the earnings-to-cash gap without inventing its cause, and avoid valuation or fraud claims. The Buffett memo was also checked against the original Buffett-only output. Streamlit AppTest verifies the NVDA selection renders all three saved memos without exceptions or audit errors.
