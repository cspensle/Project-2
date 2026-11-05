"""Lab 19: shared annual SEC evidence and deterministic investor checks."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
LAB18 = HERE.parent / "Lab18"
sys.path.insert(0, str(LAB18 / "buffett-sec/scripts"))
import buffett

INVESTORS = {"buffett": "Buffett", "wood": "Cathie Wood", "burry": "Burry"}
EXTRA_TAGS = {
    "liabilities": ["Liabilities"],
    "research_and_development": ["ResearchAndDevelopmentExpense",
                                 "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
}
EXTRA_LABELS = {"liabilities": "Liabilities", "research_and_development": "R&D",
                "rd_to_revenue": "R&D / revenue", "liabilities_to_equity": "Liabilities / equity"}


def load_snapshot(ticker, path):
    ticker = buffett.normalize_ticker(ticker)
    raw = Path(path).read_bytes()
    facts = json.loads(raw)
    source_path = Path(path).with_name(f"{ticker}_source.json")
    source = json.loads(source_path.read_text()) if source_path.exists() else {}
    digest = hashlib.sha256(raw).hexdigest()
    if source and (source.get("sha256") != digest or source.get("ticker") != ticker
                   or int(source["cik"]) != int(facts["cik"])):
        raise ValueError("SEC snapshot does not match its source record.")
    source["sha256"] = digest
    return facts, source


def select_extra(facts, metric, end):
    for tag in EXTRA_TAGS[metric]:
        values = [v for v in buffett.candidates(facts, tag, metric != "liabilities") if v["end"] == end]
        if not values:
            continue
        latest = max(values, key=lambda v: (v["filed"], v.get("accn", "")))
        tied = [v for v in values if (v["filed"], v.get("accn", "")) ==
                (latest["filed"], latest.get("accn", ""))]
        if len({(v.get("start"), v["val"]) for v in tied}) != 1:
            raise ValueError(f"Ambiguous annual {metric} facts for {end}.")
        return {"value": latest["val"], "tag": f"us-gaap:{tag}", "start": latest.get("start"),
                "end": end, "filed": latest["filed"], "accession": latest.get("accn")}
    return {"value": None, "tag": "not found", "searched_tags": EXTRA_TAGS[metric]}


def revenue_growth(rows):
    if len(rows) != 5:
        return None
    first, last = rows[0]["revenue"], rows[-1]["revenue"]
    if first is None or last is None or first <= 0 or last < 0:
        return None
    # Reject a skipped fiscal year instead of pretending the endpoints span four years.
    from datetime import date
    ends = [date.fromisoformat(r["fiscal_year_end"]) for r in rows]
    if any(not 350 <= (b - a).days <= 380 for a, b in zip(ends, ends[1:])):
        return None
    return (last / first) ** (1 / 4) - 1


def wood_checks(rows, growth_threshold=0.15):
    """Student partner exercise: explain this function without AI assistance."""
    growth = revenue_growth(rows)
    rd_ratio = rows[-1]["rd_to_revenue"] if rows else None
    return {
        f"Revenue growth a year >= {growth_threshold:.0%}":
            "not known" if growth is None else "pass" if growth >= growth_threshold else "fail",
        "R&D / revenue >= 5% latest year":
            "not known" if rd_ratio is None else "pass" if rd_ratio >= 0.05 else "fail",
    }


def burry_checks(rows):
    cash_known = len(rows) == 5 and all(r["operating_cash_flow"] is not None and
                                          r["net_income"] is not None for r in rows)
    ratio = rows[-1]["liabilities_to_equity"] if rows else None
    return {
        "Operating cash flow >= net income every year": "not known" if not cash_known else
            "pass" if all(r["operating_cash_flow"] >= r["net_income"] for r in rows) else "fail",
        "Liabilities / equity <= 2 latest year":
            "not known" if ratio is None else "pass" if ratio <= 2 else "fail",
    }


def build_panel(facts, ticker, source=None, growth_threshold=0.15):
    if not 0 <= growth_threshold <= 1:
        raise ValueError("Growth threshold must be between zero and one.")
    report = buffett.build_report(facts, ticker, source)
    for row in report["rows"]:
        extra = {m: select_extra(facts, m, row["fiscal_year_end"]) for m in EXTRA_TAGS}
        row["provenance"].update(extra)
        row.update({m: v["value"] for m, v in extra.items()})
        rd, revenue = row["research_and_development"], row["revenue"]
        liabilities, equity = row["liabilities"], row["equity"]
        row["rd_to_revenue"] = rd / revenue if rd is not None and revenue is not None and revenue > 0 else None
        row["liabilities_to_equity"] = liabilities / equity if liabilities is not None and equity is not None and equity > 0 else None
    report["growth_threshold"] = growth_threshold
    report["revenue_growth"] = revenue_growth(report["rows"])
    report["panel"] = {"buffett": report["checks"], "wood": wood_checks(report["rows"], growth_threshold),
                       "burry": burry_checks(report["rows"])}
    report["computed_at"] = datetime.now(timezone.utc).isoformat()
    return report


def format_extra(metric, value):
    if value is None:
        return "not found" if metric in EXTRA_TAGS else "not known"
    if metric == "rd_to_revenue":
        return f"{value:.2%}"
    if metric == "liabilities_to_equity":
        return f"{value:.2f}"
    return buffett.format_value(metric, value)


def table_records(report):
    records = buffett.table_records(report)
    for record, row in zip(records, report["rows"]):
        record.update({label: format_extra(m, row[m]) for m, label in EXTRA_LABELS.items()})
    return records


def panel_records(report):
    return [{"Investor": INVESTORS[i], "Check": c, "Result": v}
            for i, checks in report["panel"].items() for c, v in checks.items()]


def numeric_evidence(report):
    records = table_records(report)
    lines = [" | ".join(records[0])]
    lines.extend(" | ".join(row.values()) for row in records)
    growth = report["revenue_growth"]
    lines.append("Revenue growth a year: " + ("not known" if growth is None else f"{growth:.2%}"))
    lines.extend(f"{r['Investor']} | {r['Check']} | {r['Result']}" for r in panel_records(report))
    return "\n".join(lines)


def unsupported_numbers(memo, report):
    def key(token):
        return token if re.fullmatch(r"\d{4}-\d{2}-\d{2}", token) else buffett.number_key(token)
    allowed = {key(t) for t in buffett.numeric_tokens(numeric_evidence(report))}
    return sorted({t for t in buffett.numeric_tokens(memo) if key(t) not in allowed})


def audit_memos(memos, report):
    return {i: unsupported_numbers(memos.get(i, ""), report) for i in INVESTORS}


def render_report(report):
    lines = [f"{report['ticker']} — {report['company']}", "Monetary amounts: USD millions.",
             "Annual USD flows, 10-K only; latest filing within preferred tag; ratios use unrounded inputs.",
             numeric_evidence(report), "", "Provenance:"]
    for row in report["rows"]:
        lines.append(row["fiscal_year_end"])
        lines.extend(f"  {metric}: {json.dumps(p, sort_keys=True)}" for metric, p in row["provenance"].items())
    lines.extend(["ROE = net income / year-end equity; owner earnings = operating cash flow - capital spending.",
                  "R&D / revenue uses same-year amounts; liabilities / equity uses year-end balances.",
                  "Revenue growth = (last revenue / first revenue)^(1/4) - 1.",
                  "Source: " + json.dumps(report["source"], sort_keys=True)])
    return "\n".join(lines) + "\n"


def save_report(report, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker = report["ticker"]
    (output_dir / f"{ticker}_panel.json").write_text(json.dumps(report, indent=2) + "\n")
    (output_dir / f"{ticker}_output.txt").write_text(render_report(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker")
    parser.add_argument("--facts-file", type=Path)
    parser.add_argument("--output-dir", type=Path, default=HERE / "results")
    parser.add_argument("--wood-config", type=Path, default=HERE / "cathie-wood-sec/config.json")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    ticker = buffett.normalize_ticker(args.ticker)
    facts, source = load_snapshot(ticker, args.facts_file or LAB18 / f"results/{ticker}_companyfacts.json")
    threshold = json.loads(args.wood_config.read_text())["revenue_growth_threshold"]
    report = build_panel(facts, ticker, source, threshold)
    save_report(report, args.output_dir)
    print(render_report(report), end="")
    if args.audit:
        memos = {i: (args.output_dir / f"{ticker}_{i}_memo.md").read_text() for i in INVESTORS}
        flags = audit_memos(memos, report)
        print("Memo audit: " + json.dumps(flags))
        if any(flags.values()) or any(not m.strip() for m in memos.values()):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
