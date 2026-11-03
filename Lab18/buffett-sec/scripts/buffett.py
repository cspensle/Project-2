"""Lab 18: deterministic annual SEC facts; the AI, not this code, judges.

Only the standard library is needed. Dollar values remain USD internally;
the public table uses USD millions and ROE rounded to one decimal percent.
"""

import argparse
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen


TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
TAGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
    "net_income": ["NetIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_spending": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "equity": ["StockholdersEquity"],
}
LABELS = {
    "revenue": "Revenue", "net_income": "Net income",
    "operating_cash_flow": "Operating cash flow", "capital_spending": "Capital spending",
    "equity": "Equity", "roe": "ROE", "owner_earnings": "Owner earnings",
}


def normalize_ticker(ticker):
    ticker = ticker.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,14}", ticker):
        raise ValueError("Enter a valid SEC ticker using letters, digits, dots, or hyphens.")
    return ticker


def download_json(url, user_agent):
    if not re.search(r"\S+@\S+\.\S+", user_agent) or len(user_agent.split()) < 2:
        raise ValueError("SEC requires a User-Agent with your real name and email.")
    request = Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    with urlopen(request, timeout=45) as response:
        raw = response.read()
    return json.loads(raw), raw


def download_facts(ticker, user_agent, output_dir):
    """Save unmodified SEC responses; no synthetic fallback on download failure."""
    ticker = normalize_ticker(ticker)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    mapping, mapping_raw = download_json(TICKERS_URL, user_agent)
    match = next((row for row in mapping.values() if row["ticker"].upper() == ticker), None)
    if match is None:
        raise ValueError(f"Ticker {ticker} was not found in the SEC ticker mapping.")
    cik = int(match["cik_str"])
    time.sleep(0.2)  # Sequential requests, below SEC's rate limit.
    url = FACTS_URL.format(cik=cik)
    facts, raw = download_json(url, user_agent)
    if int(facts["cik"]) != cik:
        raise ValueError("Company-facts CIK does not match the SEC ticker mapping.")
    (output_dir / "company_tickers.json").write_bytes(mapping_raw)
    (output_dir / f"{ticker}_companyfacts.json").write_bytes(raw)
    metadata = {
        "ticker": ticker, "cik": cik, "source_url": url,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    (output_dir / f"{ticker}_source.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return facts, metadata


def annual_fact(fact):
    """Annual flow only: exclude quarters, YTD, and multiyear durations."""
    try:
        days = (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days + 1
        return 350 <= days <= 380
    except (KeyError, TypeError, ValueError):
        return False


def candidates(facts, tag, flow):
    for fact in facts.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {}).get("USD", []):
        if fact.get("form") != "10-K":
            continue
        value = fact.get("val")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            continue
        if not fact.get("end") or not fact.get("filed"):
            continue
        if flow and not annual_fact(fact):
            continue
        if not flow and fact.get("start"):
            continue
        yield fact


def fiscal_year_ends(facts):
    # Annual periods, not `fy`: comparative facts carry the filing's fiscal year.
    ends = {
        f["end"] for key in TAGS if key != "equity"
        for tag in TAGS[key] for f in candidates(facts, tag, True)
    }
    return sorted(ends)[-5:]


def select_fact(facts, metric, end):
    """Use ordered tags, then the latest filing for the requested annual period."""
    for tag in TAGS[metric]:
        available = [f for f in candidates(facts, tag, metric != "equity") if f["end"] == end]
        if available:
            latest = max(available, key=lambda f: (f["filed"], f.get("accn", "")))
            tied = [f for f in available if (f["filed"], f.get("accn", "")) ==
                    (latest["filed"], latest.get("accn", ""))]
            if len({(f.get("start"), f["val"]) for f in tied}) != 1:
                raise ValueError(f"Ambiguous annual {metric} facts for {end}; inspect the filing.")
            return {
                "value": latest["val"], "tag": f"us-gaap:{tag}",
                "start": latest.get("start"), "end": end,
                "filed": latest["filed"], "accession": latest.get("accn"),
            }
    return {"value": None, "tag": "not found", "searched_tags": [f"us-gaap:{t}" for t in TAGS[metric]]}


def year_row(facts, end):
    """Function to explain during the lab's student-only partner exercise."""
    selected = {metric: select_fact(facts, metric, end) for metric in TAGS}
    row = {"fiscal_year_end": end, "provenance": selected}
    row.update({metric: item["value"] for metric, item in selected.items()})
    equity, income = row["equity"], row["net_income"]
    row["roe"] = income / equity if income is not None and equity is not None and equity > 0 else None
    ocf, capex = row["operating_cash_flow"], row["capital_spending"]
    row["owner_earnings"] = ocf - capex if ocf is not None and capex is not None else None
    return row


def checks(rows):
    def every(metric, predicate):
        if len(rows) != 5 or any(r[metric] is None for r in rows):
            return "not known"
        return "pass" if all(predicate(r[metric]) for r in rows) else "fail"

    growth = "not known"
    if len(rows) == 5 and rows[0]["owner_earnings"] is not None and rows[-1]["owner_earnings"] is not None:
        growth = "pass" if rows[-1]["owner_earnings"] > rows[0]["owner_earnings"] else "fail"
    return {
        "ROE >= 15% every year": every("roe", lambda v: v >= 0.15),
        "Owner earnings positive every year": every("owner_earnings", lambda v: v > 0),
        "Owner earnings grew, first year to last": growth,
    }


def format_value(metric, value):
    if value is None:
        return "not known" if metric == "roe" else "not found"
    if metric == "roe":
        return f"{value:.1%}"
    millions = Decimal(str(value)) / Decimal(1_000_000)
    return f"{millions:,.0f}" if millions == millions.to_integral() else f"{millions:,.3f}"


def table_records(report):
    return [{"Fiscal year end": row["fiscal_year_end"], **{
        LABELS[key]: format_value(key, row[key]) for key in LABELS
    }} for row in report["rows"]]


def numeric_evidence(report):
    """Only table numbers, fiscal-year labels, and the printed check threshold."""
    return "\n".join(" | ".join(row.values()) for row in table_records(report)) + "\n" + "\n".join(report["checks"])


# Keep percentages distinct from amounts; support signs, decimals, comma groups,
# scientific notation, dates, and digits in labels such as FY2026 and 10-K.
NUMBER = re.compile(r"[+\-−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][+\-]?\d+)?\s*%?")


def number_key(token):
    token = token.strip().replace(",", "").replace("−", "-")
    percent = token.endswith("%")
    value = Decimal(token.rstrip("% "))
    return value, percent


def numeric_tokens(text):
    # Dates yield the full date and its year, so fiscal-year mentions are allowed.
    dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)
    rest = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", text)
    return [m.group().strip() for m in NUMBER.finditer(rest)] + dates + [d[:4] for d in dates]


def unsupported_numbers(memo, report):
    def key(token):
        return token if re.fullmatch(r"\d{4}-\d{2}-\d{2}", token) else number_key(token)
    allowed = {key(token) for token in numeric_tokens(numeric_evidence(report))}
    return sorted({token for token in numeric_tokens(memo) if key(token) not in allowed})


def build_report(facts, ticker, metadata=None):
    rows = [year_row(facts, end) for end in fiscal_year_ends(facts)]
    if not rows:
        raise ValueError("No annual USD facts from 10-K filings found under the lab's allowed tags.")
    return {
        "ticker": normalize_ticker(ticker), "company": facts.get("entityName", "not found"),
        "cik": facts["cik"], "units": "USD millions; ROE percent",
        "source": metadata or {}, "rows": rows, "checks": checks(rows),
    }


def render_report(report):
    records = table_records(report)
    headers = list(records[0])
    lines = [f"{report['ticker']} — {report['company']}", "USD millions; ROE uses year-end equity.",
             "Annual flows: 350–380 days. Latest 10-K filing wins within each selected tag.",
             " | ".join(headers)]
    lines.extend(" | ".join(row.values()) for row in records)
    lines.extend(f"{label}: {value}" for label, value in report["checks"].items())
    if len(report["rows"]) != 5:
        lines.append("Incomplete annual history: fewer than five fiscal years available.")
    lines.append("\nXBRL provenance (derived measures list operand tags):")
    for row in report["rows"]:
        lines.append(row["fiscal_year_end"])
        for metric, source in row["provenance"].items():
            lines.append(f"  {LABELS[metric]}: {source['tag']}; period {source.get('start', 'instant')} to "
                         f"{row['fiscal_year_end']}; filed {source.get('filed', 'not found')}; "
                         f"accession {source.get('accession', 'not found')}")
            if source.get("searched_tags"):
                lines.append("    Searched: " + ", ".join(source["searched_tags"]))
        p = row["provenance"]
        lines.append(f"  ROE = {p['net_income']['tag']} / {p['equity']['tag']}")
        lines.append(f"  Owner earnings = {p['operating_cash_flow']['tag']} - {p['capital_spending']['tag']}")
    lines.append("\nSource: " + FACTS_URL.format(cik=int(report["cik"])))
    lines.append("Download: " + report["source"].get("downloaded_at", "unknown (local input)"))
    lines.append("SHA-256: " + report["source"].get("sha256", "not recorded"))
    return "\n".join(lines) + "\n"


def save_report(report, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker = report["ticker"]
    (output_dir / f"{ticker}_report.json").write_text(json.dumps(report, indent=2) + "\n")
    (output_dir / f"{ticker}_output.txt").write_text(render_report(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker")
    parser.add_argument("--user-agent", default=os.environ.get("SEC_USER_AGENT", ""))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--facts-file", type=Path)
    parser.add_argument("--memo", type=Path)
    args = parser.parse_args()
    ticker = normalize_ticker(args.ticker)
    if args.facts_file:
        raw = args.facts_file.read_bytes()
        facts = json.loads(raw)
        source_file = args.facts_file.with_name(f"{ticker}_source.json")
        metadata = json.loads(source_file.read_text()) if source_file.exists() else {}
        digest = hashlib.sha256(raw).hexdigest()
        if metadata and (metadata.get("sha256") != digest or metadata.get("ticker") != ticker
                         or int(metadata["cik"]) != int(facts["cik"])):
            raise ValueError("Saved SEC facts do not match their source record.")
        metadata["sha256"] = digest
    else:
        facts, metadata = download_facts(ticker, args.user_agent, args.output_dir)
    report = build_report(facts, ticker, metadata)
    save_report(report, args.output_dir)
    print(render_report(report), end="")
    if args.memo:
        flags = unsupported_numbers(args.memo.read_text(), report)
        print("Memo numeric audit: " + (", ".join(flags) if flags else "no unsupported numbers"))
        if flags:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
