"""Checks financial boundaries, missing data, the COST answer and all memo flags."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import panel


def rows():
    return [{"fiscal_year_end": f"{year}-12-31", "revenue": 100 * 1.2 ** i,
             "rd_to_revenue": 0.05, "liabilities_to_equity": 2,
             "operating_cash_flow": 20, "net_income": 20}
            for i, year in enumerate(range(2021, 2026))]


class PanelTests(unittest.TestCase):
    def test_wood_missing_inputs_and_nonpositive_revenue(self):
        data = rows()
        self.assertEqual(list(panel.wood_checks(data).values()), ["pass", "pass"])
        data[-1]["rd_to_revenue"] = None
        data[0]["revenue"] = None
        self.assertEqual(list(panel.wood_checks(data).values()), ["not known", "not known"])
        for value in (0, -100):
            data[0]["revenue"] = value
            self.assertIsNone(panel.revenue_growth(data))

    def test_missing_history_and_skipped_year(self):
        self.assertIsNone(panel.revenue_growth(rows()[:4]))
        data = rows()
        data[-1]["fiscal_year_end"] = "2026-12-31"
        self.assertIsNone(panel.revenue_growth(data))

    def test_unrounded_boundary(self):
        data = rows()
        data[-1]["rd_to_revenue"] = 0.049999
        data[-1]["liabilities_to_equity"] = 2.000001
        self.assertEqual(list(panel.wood_checks(data).values())[1], "fail")
        self.assertEqual(list(panel.burry_checks(data).values()), ["pass", "fail"])
        threshold = panel.revenue_growth(data)
        self.assertEqual(list(panel.wood_checks(data, threshold).values())[0], "pass")
        self.assertEqual(list(panel.wood_checks(data, threshold + 0.000001).values())[0], "fail")

    def test_burry_missing_precedes_failure(self):
        data = rows()
        data[0]["operating_cash_flow"] = 1
        self.assertEqual(list(panel.burry_checks(data).values())[0], "fail")
        data[1]["net_income"] = None
        self.assertEqual(list(panel.burry_checks(data).values())[0], "not known")
        self.assertEqual(list(panel.burry_checks(data[:4]).values())[0], "not known")

    def test_extra_selection_fallback_annual_latest_and_instant(self):
        def fact(value, start=None, filed="2026-02-01", form="10-K"):
            return {"val": value, "start": start, "end": "2025-12-31", "filed": filed, "form": form}
        data = {"facts": {"us-gaap": {
            "Liabilities": {"units": {"USD": [fact(200), fact(210, filed="2027-02-01"),
                                                      fact(999, start="2025-01-01")] }},
            "ResearchAndDevelopmentExpense": {"units": {"USD": [fact(999, "2025-10-01")]}},
            "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost": {"units": {"USD": [
                fact(5, "2025-01-01"), fact(6, "2025-01-01", "2027-02-01"),
                fact(999, "2025-01-01", "2028-02-01", "10-Q")] }},
        }}}
        self.assertEqual(panel.select_extra(data, "liabilities", "2025-12-31")["value"], 210)
        self.assertEqual(panel.select_extra(data, "research_and_development", "2025-12-31")["value"], 6)


class CostValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts, cls.source = panel.load_snapshot("COST", panel.LAB18 / "results/COST_companyfacts.json")
        cls.report = panel.build_panel(cls.facts, "COST", cls.source)

    def test_known_answer_from_raw_facts(self):
        r = self.report
        self.assertEqual([f"{x['liabilities_to_equity']:.2f}" for x in r["rows"]],
                         ["2.11", "1.75", "1.96", "1.64", "1.49"])
        self.assertTrue(all(x["research_and_development"] is None for x in r["rows"]))
        self.assertEqual(f"{r['revenue_growth']:.2%}", "7.51%")
        self.assertEqual(list(r["panel"]["buffett"].values()), ["pass"] * 3)
        self.assertEqual(list(r["panel"]["wood"].values()), ["fail", "not known"])
        self.assertEqual(list(r["panel"]["burry"].values()), ["pass"] * 2)

    def test_threshold_probe(self):
        config = json.loads((HERE / "cathie-wood-sec/probe-config.json").read_text())
        probe = panel.build_panel(self.facts, "COST", self.source, config["revenue_growth_threshold"])
        self.assertEqual(list(probe["panel"]["wood"].values()), ["pass", "not known"])
        self.assertEqual(probe["rows"], self.report["rows"])

    def test_nonpositive_equity_and_missing_liabilities(self):
        for equity in (0, -1):
            data = deepcopy(self.facts)
            for v in data["facts"]["us-gaap"]["StockholdersEquity"]["units"]["USD"]:
                v["val"] = equity
            report = panel.build_panel(data, "COST")
            self.assertTrue(all(r["liabilities_to_equity"] is None for r in report["rows"]))
            self.assertEqual(list(report["panel"]["burry"].values())[1], "not known")
        data = deepcopy(self.facts)
        del data["facts"]["us-gaap"]["Liabilities"]
        report = panel.build_panel(data, "COST")
        self.assertEqual(list(report["panel"]["burry"].values())[1], "not known")

    def test_all_memos_and_injected_numbers(self):
        memos = {i: (HERE / f"results/COST_{i}_memo.md").read_text() for i in panel.INVESTORS}
        self.assertEqual(panel.audit_memos(memos, self.report), {i: [] for i in panel.INVESTORS})
        for investor in panel.INVESTORS:
            injected = {**memos, investor: memos[investor] + " Unsupported 987.654321%."}
            self.assertEqual(panel.audit_memos(injected, self.report)[investor], ["987.654321%"])
        self.assertEqual(panel.unsupported_numbers("Negative growth -7.51%", self.report), ["-7.51%"])
        self.assertEqual(panel.unsupported_numbers("Amount 7.51", self.report), ["7.51"])


if __name__ == "__main__":
    unittest.main()
