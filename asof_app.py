"""Lab 17: live FRED/ALFRED point-in-time rates audit.

Run from the course workspace with:
    .venv/bin/python -m streamlit run ColinSpensley/MSFT/asof_app.py
"""

from datetime import date
from io import StringIO
import re

import pandas as pd
import requests
import streamlit as st


SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Effective federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year fixed mortgage rate",
}
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_CSV = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"


def _download(url: str, series_id: str, vintage: date | None = None) -> pd.Series:
    params = {"id": series_id}
    if vintage is not None:
        params["vintage_date"] = vintage.isoformat()
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    frame = pd.read_csv(StringIO(response.text))
    if frame.shape[1] != 2 or frame.columns[0] not in ("observation_date", "DATE"):
        raise ValueError(f"Unexpected CSV format for {series_id}")
    dates = pd.to_datetime(frame.iloc[:, 0], errors="raise")
    values = pd.to_numeric(frame.iloc[:, 1].replace(".", pd.NA), errors="coerce")
    observations = pd.Series(values.to_numpy(), index=dates, name=series_id)
    return observations.dropna().sort_index()


@st.cache_data(ttl=3600, show_spinner=False)
def download_today(series_id: str) -> pd.Series:
    """Get the current FRED vintage; cache for one hour."""
    return _download(FRED_CSV, series_id)


@st.cache_data(ttl=3600, show_spinner=False)
def download_asof(series_id: str, vintage: date) -> pd.Series:
    """Get only values knowable at the requested ALFRED vintage date."""
    return _download(ALFRED_CSV, series_id, vintage)


def summarize(series_id: str, current: pd.Series, known: pd.Series) -> dict:
    if current.empty or known.empty:
        raise ValueError(f"No observations returned for {series_id}")
    last_known_date = known.index[-1]
    shared = current.index.intersection(known.index)
    revised = int((current.loc[shared] != known.loc[shared]).sum())
    late = int((current.index > last_known_date).sum())
    return {
        "FRED series": f"https://fred.stlouisfed.org/series/{series_id}",
        "Last date known then": last_known_date.date(),
        "Value known then": float(known.iloc[-1]),
        "Last date today": current.index[-1].date(),
        "Value today": float(current.iloc[-1]),
        "Later values": late,
        "Revised shared dates": revised,
    }


def main() -> None:
    st.set_page_config(page_title="Rates as known on a date", layout="wide")
    st.title("Rates as known on a date")
    st.caption(
        "Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, "
        f"downloaded {date.today().isoformat()}; built with AI help, a learning "
        "demonstration, not investment advice."
    )

    selected = st.sidebar.multiselect(
        "Rates series",
        options=list(SERIES),
        default=list(SERIES),
        format_func=lambda series_id: f"{series_id} — {SERIES[series_id]}",
    )
    additional = st.sidebar.text_input("Add a FRED series ID", placeholder="PAYEMS")
    start = st.sidebar.date_input("Start date", value=date(2020, 1, 1))
    vintage = st.sidebar.date_input("As known on", value=date.today(), max_value=date.today())

    if additional:
        series_id = additional.strip().upper()
        if re.fullmatch(r"[A-Z0-9_]+", series_id):
            if series_id not in selected:
                selected.append(series_id)
        else:
            st.sidebar.error("Use a FRED series ID with letters, numbers, or underscores.")

    rows = []
    for series_id in selected:
        st.subheader(f"{series_id} — {SERIES.get(series_id, 'FRED series')}")
        try:
            current = download_today(series_id)
            known = download_asof(series_id, vintage)
            row = summarize(series_id, current, known)
        except (requests.RequestException, pd.errors.ParserError, ValueError, IndexError) as exc:
            st.error(f"Could not load {series_id}: {exc}")
            continue

        st.line_chart(current.loc[current.index >= pd.Timestamp(start)])
        st.caption(
            f"Last observation known on {vintage.isoformat()}: "
            f"{row['Last date known then']} = {row['Value known then']:,.2f}"
        )
        rows.append(row)

    if rows:
        st.subheader("Point-in-time comparison")
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            column_config={"FRED series": st.column_config.LinkColumn("FRED series")},
            width="stretch",
        )
        st.caption(
            "Later values count observations measured after the last date known then. "
            "Revised shared dates count values changed on dates present in both downloads."
        )


if __name__ == "__main__":
    main()
