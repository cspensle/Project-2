# COST — Lab 18 validation

Validated on 3 November 2026 using the user's saved SEC download, timestamp
`2026-11-03T22:37:19.553980+00:00`. The script verified its SHA-256 against
`COST_source.json` before recomputing the report. No new download was needed.

The recomputed table matches every fiscal-year-end date and every displayed
financial value in the [official Lab 18 answer](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md#v--prove-it-on-the-known-answer),
checked against the course page on the validation date. Amounts below are USD
millions; ROE uses year-end equity and is rounded to one decimal percent.

| Fiscal year end | Revenue | Net income | Operating cash flow | Capital spending | Equity | ROE | Owner earnings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022-08-28 | 226,954 | 5,844 | 7,392 | 3,891 | 20,642 | 28.3% | 3,501 |
| 2023-09-03 | 242,290 | 6,292 | 11,068 | 4,323 | 25,058 | 25.1% | 6,745 |
| 2024-09-01 | 254,453 | 7,367 | 11,339 | 4,710 | 23,622 | 31.2% | 6,629 |
| 2025-08-31 | 275,235 | 8,099 | 13,335 | 5,498 | 29,164 | 27.8% | 7,837 |
| 2026-08-30 | 303,154 | 9,226 | 15,817 | 6,435 | 35,803 | 25.8% | 9,382 |

All three computed checks pass: ROE at least 15% every year, positive owner
earnings every year, and first-to-last growth in owner earnings. Growth is an
endpoint check; the FY2024 decline does not fail that test.

## Verification performed

- Recomputed [script output](COST_output.txt) from the saved raw company facts;
  tags, periods, filing dates, and accessions are retained in the output.
- The existing COST known-answer test and six extraction tests passed.
- Wrote the [Buffett-inspired memo](COST_memo.md) from the actual script output.
  Its verdict is **watch it**: the financial screens pass, while evidence of a
  durable moat and management quality is outside this limited dataset.
- The command-line memo audit reported no unsupported numbers. Manually
  checked that the memo's figures refer to the correct metrics and fiscal years.
- Streamlit AppTest rendered the chart, financial table, checks, saved memo,
  and passing numeric audit without an application exception.
- AppTest added `ROE is 40.0%.` to the memo editor and confirmed the warning.
  This was an automated probe; it did not change the saved memo or represent
  the student's own manual classroom exercise.

## Remaining work

JPM data and its missing-value probe are still pending. The student's personal
trust decision, fresh-chat comparison, no-AI partner exercises, and quiz/GitHub
checkout are not claimed as completed. This validation and memo are AI-assisted.
