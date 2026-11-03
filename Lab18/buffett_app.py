"""Run: .venv/bin/python -m streamlit run 'ColinSpensley/Project 2/Lab18/buffett_app.py'"""

import json
import os
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "buffett-sec" / "scripts"))
from buffett import (build_report, download_facts, normalize_ticker, render_report,
                     save_report, table_records, unsupported_numbers)

RESULTS = HERE / "results"
st.set_page_config(page_title="Lab 18 · Buffett business review", layout="wide")
st.title("Buffett business review")
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")

ticker_input = st.text_input("SEC ticker", "COST", help="Try COST for the known answer or JPM for the missing-data probe.")
try:
    ticker = normalize_ticker(ticker_input)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

with st.expander("Download or refresh SEC data"):
    user_agent = st.text_input("SEC User-Agent (your name and email)", os.environ.get("SEC_USER_AGENT", ""))
    if st.button("Download latest annual facts"):
        try:
            with st.spinner("Downloading from SEC EDGAR…"):
                facts, metadata = download_facts(ticker, user_agent, RESULTS)
                save_report(build_report(facts, ticker, metadata), RESULTS)
            st.success("SEC facts downloaded and report computed.")
        except Exception as exc:
            st.error(f"Download failed: {exc}")
            st.stop()

report_path = RESULTS / f"{ticker}_report.json"
if not report_path.exists():
    st.info("Download this ticker above to compute its report. Then ask Codex to use the buffett-sec skill to write its memo.")
    st.stop()
report = json.loads(report_path.read_text())
st.subheader(f"{report['company']} ({ticker})")
source = report.get("source", {})
st.caption(f"Saved SEC download: {source.get('downloaded_at', 'unknown')} · Monetary amounts in USD millions.")
st.markdown(f"[SEC company facts]({source.get('source_url', 'https://data.sec.gov')})")

chart = pd.DataFrame([{
    "Fiscal year end": row["fiscal_year_end"],
    "Owner earnings": None if row["owner_earnings"] is None else row["owner_earnings"] / 1_000_000,
    "Net income": None if row["net_income"] is None else row["net_income"] / 1_000_000,
} for row in report["rows"]]).set_index("Fiscal year end")
st.line_chart(chart, y_label="USD millions")
if any(row["owner_earnings"] is None for row in report["rows"]):
    st.warning("Owner earnings are not found for one or more years; missing points are not zero.")
st.dataframe(pd.DataFrame(table_records(report)), hide_index=True, width="stretch")
st.caption("ROE = net income ÷ year-end equity. Owner earnings = operating cash flow − total capital spending.")
st.subheader("Computed checks")
st.dataframe(pd.DataFrame([{"Check": key, "Result": value} for key, value in report["checks"].items()]),
             hide_index=True, width="stretch")
with st.expander("XBRL tags, filing dates, and exact script output"):
    st.text(render_report(report))

st.subheader("Buffett-inspired memo")
st.caption("AI simulation. The judgment is written by the model after it reads the script output.")
memo_path = RESULTS / f"{ticker}_memo.md"
initial_memo = memo_path.read_text() if memo_path.exists() else ""
memo = st.text_area("Memo editor — try adding ROE of 40.0%", initial_memo, height=250, key=f"memo_{ticker}")
if memo.strip():
    flags = unsupported_numbers(memo, report)
    if flags:
        st.error("Numbers not printed in the computed table/checks: " + ", ".join(flags))
    else:
        st.success("Numeric audit passed: every numeric token appears in the computed table/checks.")
    st.caption("This checks numeric presence, not the correctness of a metric, year, unit, or interpretation. Review the claims too.")
    st.markdown(memo)
    if st.button("Save memo", disabled=bool(flags)):
        memo_path.write_text(memo.rstrip() + "\n")
        st.success(f"Saved {memo_path.name}")
    st.download_button("Download memo (.md)", memo, file_name=f"{ticker}_memo.md", mime="text/markdown")
else:
    st.info(f"Ask Codex to use buffett-sec on {ticker}, save results/{ticker}_memo.md, then reload; or paste the resulting memo here.")
st.download_button("Download computed output", render_report(report), file_name=f"{ticker}_output.txt")
