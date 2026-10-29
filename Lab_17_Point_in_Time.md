# Lab 17 — Point-in-Time Audit

**Source:** [Official FIN43900 Lab 17 instructions](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-17-point-in-time.md)  
**App:** [asof_app.py](asof_app.py)  
**Run:** `.venv/bin/python -m streamlit run ColinSpensley/MSFT/asof_app.py` from the course workspace.  
**Live download and verification date:** 29 October 2026.

## App and known-answer check

The app downloads current FRED CSV and date-specific ALFRED CSV independently, caches both, charts each selected series, and reports the last observation known on the selected date, the current last observation, later observations, and revised values on shared observation dates. It starts with all four required rates. A typed valid series ID can be added; a failed series reports its own error so the other series can still display. The source URLs are linked in the comparison table.

The live 5 October 2026 vintage matched all four official anchors:

| Series | Last observation then | Value then |
|---|---|---:|
| BAA | September 2026 | 6.47 |
| FEDFUNDS | September 2026 | 3.75 |
| DGS10 | 2 October 2026 | 5.28 |
| MORTGAGE30US | 1 October 2026 | 7.28 |

The PAYEMS probe for 15 January 2025 returned **December 2024 = 159,536 thousand** as known then. Its current December 2024 observation was **159,044 thousand**; **381 shared observation dates** differed between the two full downloads. These counts are point-in-time comparisons at the download date, not fixed historical facts. The Streamlit page rendered with four chart elements and a comparison table without an exception.

## Student universe and proposed series data card

The student selected VOO, BND, and VGT; their verified full names and roles are in [the universe draft](Project_2_Universe_DRAFT.md). The following **DFII10 series is AI-proposed**, not claimed as the student's prework choice or personal judgment.

- **Series ID and source:** [DFII10 on FRED](https://fred.stlouisfed.org/series/DFII10), sourced from the Federal Reserve Board's [H.15 Selected Interest Rates release](https://www.federalreserve.gov/releases/h15/).
- **Measure:** Market yield on U.S. Treasury inflation-indexed securities at 10-year constant maturity, quoted on an investment basis.
- **Units and frequency:** Percent per annum, daily, not seasonally adjusted. This is a yield, not an ETF return.
- **Why it could matter:** Changes in the real yield affect bond discount rates and provide a plausible valuation-rate input for VOO and the technology-heavy VGT. This is a causal hypothesis to test in Project 2, not an established return predictor.
- **Publication lag:** H.15 is posted on business days at 4:15 p.m. ET. At the 30 September 2026 ALFRED vintage, the latest available DFII10 observation was **29 September = 2.91%**. At the 29 October download, the latest current observation was **28 October = 2.67%**. For a strategy trading before the release, use a vintage and observation available before the trade; a conservative daily backtest would act no earlier than the next trading day after publication.
- **Revisions:** Comparing the 30 September 2026 vintage with the 29 October current CSV found **zero changed values on 5,940 shared dates**. That is evidence for this comparison only; it does not prove the series is never revised. The 29 October file contained **20 later observations**.
- **Download date:** 29 October 2026, from FRED and ALFRED public CSV downloads.
- **Three values for the student to check personally against the FRED page:** 26 October 2026 = 2.66%, 27 October = 2.64%, 28 October = 2.67%. These came from the current CSV; the personal page check is still pending.

**AI-proposed Project 2 call for student review:** *Admit DFII10 only with the publication timing enforced and the ALFRED vintage for every decision date. Quarantine it if the needed vintage or release timing cannot be verified, or if a later audit reveals materially different revisions.* The student's own final call remains pending.

## Student and partner work still required

1. Confirm DFII10 as the student's selected FRED series, or supply the ID chosen during prework. The VOO/BND/VGT universe is recorded.
2. Personally check three values against the FRED page and confirm the source's units, frequency, release timing, and revisions.
3. Explain the date-specific download function line by line to the partner without AI, answer one question from the code, and exchange roles.
4. Record the partner's least-trusted field (publication date, revisions, or units), then answer it in two sentences with app or FRED evidence.
5. Make the individual **admit / quarantine / reject** call for Project 2, including the as-of rule and a condition that would change the call. Explain the publication lag and what a backtest on today's values would overstate.
6. Complete the Brightspace Lab 17 quiz attempt and submit GitHub links to the `.py` and `.md` files. The quiz and partner exchange are not represented as completed here.

This record is AI-assisted. The student's own interpretation, source checks, partner exchange, and submission remain their responsibility.
