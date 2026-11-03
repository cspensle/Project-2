"""Financial extraction and missing-data invariants; run with unittest."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "buffett-sec" / "scripts"))
from buffett import (TAGS, annual_fact, build_report, checks, select_fact,
                     unsupported_numbers, year_row)


def fact(value, *, start="2025-01-01", end="2025-12-31", filed="2026-02-01", form="10-K"):
    result = {"val": value, "end": end, "filed": filed, "form": form, "accn": "test-accession"}
    if start:
        result["start"] = start
    return result


def sample():
    gaap = {}
    for metric, tags in TAGS.items():
        gaap[tags[0]] = {"units": {"USD": [fact(100, start=None if metric == "equity" else "2025-01-01")]}}
    return {"cik": 1, "entityName": "Synthetic test fixture", "facts": {"us-gaap": gaap}}


class ExtractionTests(unittest.TestCase):
    def test_annual_filters_latest_filing_and_period_label(self):
        data = sample()
        entries = data["facts"]["us-gaap"][TAGS["net_income"][0]]["units"]["USD"]
        entries.extend([fact(999, start="2025-10-01", filed="2026-03-01"),
                        fact(888, form="10-Q", filed="2026-04-01"),
                        fact(120, filed="2027-02-01")])
        entries[-1]["fy"] = 2026
        chosen = select_fact(data, "net_income", "2025-12-31")
        self.assertEqual(chosen["value"], 120)
        self.assertEqual(build_report(data, "TEST")["rows"][0]["fiscal_year_end"], "2025-12-31")

    def test_53_week_year_and_multiyear_rejection(self):
        self.assertTrue(annual_fact(fact(1, start="2022-08-29", end="2023-09-03")))
        self.assertFalse(annual_fact(fact(1, start="2024-01-01")))

    def test_fallback_and_missing(self):
        data = sample()
        gaap = data["facts"]["us-gaap"]
        del gaap[TAGS["capital_spending"][0]]
        row = year_row(data, "2025-12-31")
        self.assertIsNone(row["capital_spending"])
        self.assertIsNone(row["owner_earnings"])
        self.assertEqual(list(checks([row] * 5).values())[1:], ["not known", "not known"])
        gaap[TAGS["capital_spending"][1]] = {"units": {"USD": [fact(25)]}}
        self.assertEqual(year_row(data, "2025-12-31")["owner_earnings"], 75)

    def test_zero_negative_equity_and_missing_income(self):
        for value in [0, -100]:
            data = sample()
            data["facts"]["us-gaap"]["StockholdersEquity"]["units"]["USD"][0]["val"] = value
            self.assertIsNone(year_row(data, "2025-12-31")["roe"])
        data = sample()
        del data["facts"]["us-gaap"]["NetIncomeLoss"]
        self.assertIsNone(year_row(data, "2025-12-31")["roe"])

    def test_thresholds_use_unrounded_numbers(self):
        row = {"roe": 0.14999, "owner_earnings": 0}
        self.assertEqual(list(checks([row] * 5).values()), ["fail", "fail", "fail"])
        row = {"roe": 0.15, "owner_earnings": 1}
        rows = [deepcopy(row) for _ in range(5)]
        rows[-1]["owner_earnings"] = 2
        self.assertEqual(list(checks(rows).values()), ["pass", "pass", "pass"])
        self.assertTrue(all(v == "not known" for v in checks(rows[:4]).values()))

    def test_numeric_audit(self):
        report = build_report(sample(), "TEST")
        self.assertEqual(unsupported_numbers("In FY2025 ROE was 100.0%.", report), [])
        self.assertEqual(unsupported_numbers("ROE was 40.0%.", report), ["40.0%"])
        self.assertEqual(unsupported_numbers("ROE was -100.0%.", report), ["-100.0%"])
        self.assertEqual(unsupported_numbers("100.0 is an amount, not a percent.", report), ["100.0"])


@unittest.skipUnless((HERE / "results/COST_report.json").exists(), "Live SEC reports not downloaded")
class LiveLabProbes(unittest.TestCase):
    def test_costco_known_answer(self):
        report = json.loads((HERE / "results/COST_report.json").read_text())
        expected = [
            ("2022-08-28", 226954, 5844, 7392, 3891, 20642, 28.3, 3501),
            ("2023-09-03", 242290, 6292, 11068, 4323, 25058, 25.1, 6745),
            ("2024-09-01", 254453, 7367, 11339, 4710, 23622, 31.2, 6629),
            ("2025-08-31", 275235, 8099, 13335, 5498, 29164, 27.8, 7837),
            ("2026-08-30", 303154, 9226, 15817, 6435, 35803, 25.8, 9382),
        ]
        actual = [(r["fiscal_year_end"], *(r[k] / 1_000_000 for k in TAGS),
                   round(r["roe"] * 100, 1), r["owner_earnings"] / 1_000_000) for r in report["rows"]]
        self.assertEqual(actual, expected)
        self.assertEqual(list(report["checks"].values()), ["pass"] * 3)

    def test_jpm_missing_values(self):
        report = json.loads((HERE / "results/JPM_report.json").read_text())
        self.assertTrue(all(r["capital_spending"] is None and r["owner_earnings"] is None for r in report["rows"]))
        self.assertEqual(list(report["checks"].values())[1:], ["not known", "not known"])

    def test_saved_memos_and_injected_roe(self):
        for ticker in ["COST", "JPM"]:
            report = json.loads((HERE / f"results/{ticker}_report.json").read_text())
            memo = (HERE / f"results/{ticker}_memo.md").read_text()
            self.assertEqual(unsupported_numbers(memo, report), [])
            self.assertIn("40.0%", unsupported_numbers(memo + " ROE is 40.0%.", report))


if __name__ == "__main__":
    unittest.main()
