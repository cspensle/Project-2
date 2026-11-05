"""Three-persona panel embedded in the existing Buffett Streamlit app."""
import json
import re

import pandas as pd
import streamlit as st

from panel import (HERE, INVESTORS, audit_memos, build_panel, load_snapshot,
                   panel_records, render_report, table_records)


def render_panel(ticker, raw_path):
    results = HERE / "results"
    default_threshold = json.loads((HERE / "cathie-wood-sec/config.json").read_text())["revenue_growth_threshold"]
    st.subheader("Legend panel")
    threshold_pct = st.selectbox("Cathie Wood revenue-growth threshold", [15, 5],
                                index=0 if default_threshold == 0.15 else 1,
                                format_func=lambda n: f"{n}%" )
    try:
        facts, source = load_snapshot(ticker, raw_path)
        report = build_panel(facts, ticker, source, threshold_pct / 100)
    except (OSError, ValueError, KeyError) as exc:
        st.error(f"Panel could not load SEC evidence: {exc}")
        return
    st.dataframe(pd.DataFrame(table_records(report)), hide_index=True, width="stretch")
    growth = report["revenue_growth"]
    st.metric("Annual revenue growth, first to last fiscal year",
              "not known" if growth is None else f"{growth:.2%}")
    st.dataframe(pd.DataFrame(panel_records(report)), hide_index=True, width="stretch")
    st.caption("Missing R&D remains not found; its ratio and check remain not known. All checks use unrounded values.")
    if threshold_pct / 100 != default_threshold:
        st.info("Threshold probe active. The saved memos below were written for the retained threshold; their judgments have not been regenerated.")
    with st.expander("Panel evidence and provenance"):
        st.text(render_report(report))

    saved_path = results / f"{ticker}_panel.json"
    if saved_path.exists():
        saved = json.loads(saved_path.read_text())
        if saved["source"].get("sha256") != source.get("sha256"):
            st.warning("SEC facts have changed since these memos were written. Regenerate the memos before relying on their judgments.")
    st.subheader("Investor memos")
    st.caption("AI learning simulations written after reviewing script output. These are not the investors' actual opinions.")
    memos = {}
    columns = st.columns(3)
    for column, (investor, name) in zip(columns, INVESTORS.items()):
        path = results / f"{ticker}_{investor}_memo.md"
        initial = path.read_text() if path.exists() else ""
        if not initial and investor == "buffett":
            original = raw_path.with_name(f"{ticker}_memo.md")
            initial = original.read_text() if original.exists() else ""
        with column:
            st.markdown(f"### {name}")
            memos[investor] = st.text_area(f"{name} memo editor", initial, height=280,
                                          key=f"panel_memo_{ticker}_{investor}")
            memo = memos[investor]
            verdict = re.search(r"\*\*Verdict:\s*(.*?)\*\*", memo)
            st.markdown(f"**Verdict:** {verdict.group(1) if verdict else 'Pending model judgment'}")
            if memo.strip():
                st.markdown(memo)
            else:
                st.info(f"Ask Codex to run the {name} skill on this snapshot and save its memo.")

    flags = audit_memos(memos, report)
    for column, (investor, name) in zip(columns, INVESTORS.items()):
        with column:
            if flags[investor]:
                st.error(f"{name}: numbers not printed in the table/checks: " + ", ".join(flags[investor]))
            elif memos[investor].strip():
                st.success(f"{name}: numeric audit passed.")
            if st.button(f"Save {name} memo", disabled=bool(flags[investor]) or not memos[investor].strip()):
                results.mkdir(parents=True, exist_ok=True)
                (results / f"{ticker}_{investor}_memo.md").write_text(memos[investor].rstrip() + "\n")
                st.success("Memo saved.")
            st.download_button(f"Download {name} memo", memos[investor],
                               file_name=f"{ticker}_{investor}_memo.md", mime="text/markdown")
    if all(m.strip() for m in memos.values()) and not any(flags.values()):
        st.success("All three memos passed the numeric audit.")
    st.caption("The flag checks numeric presence, not the correctness of the metric, fiscal year, scale or interpretation. Review those separately.")
    st.download_button("Download panel output", render_report(report), file_name=f"{ticker}_panel_output.txt")
