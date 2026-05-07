import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _path(relative):
    return os.path.join(BASE_DIR, relative)

def _get_db_conn():
    """Returns a psycopg2 connection.
    On Streamlit Cloud: reads from st.secrets['postgres'].
    Locally: falls back to .env file.
    """
    import psycopg2, warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    try:
        # Streamlit Cloud — secrets injected via the dashboard
        s = st.secrets["postgres"]
        return psycopg2.connect(
            host=s["PGHOST"], user=s["PGUSER"],
            password=s["PGPASSWORD"], port=int(s["PGPORT"]),
            dbname=s["PGDATABASE"], sslmode="require"
        )
    except (KeyError, FileNotFoundError):
        # Local — load from .env
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, '.env'))
        return psycopg2.connect(
            host=os.environ["PGHOST"], user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"], port=int(os.environ["PGPORT"]),
            dbname=os.environ["PGDATABASE"], sslmode="require"
        )


@st.cache_data(ttl=3600)
def load_gdp_data():
    conn = _get_db_conn()
    query = """
        SELECT
            to_char(o.period, 'YYYY-MM-DD')  AS "Date",
            s.name                             AS "Name",
            s.line                             AS "line",
            s.depth                            AS "depth",
            o.value                            AS "Values",
            ps.name                            AS "parent_name",
            s.parent_line                      AS "parent_line",
            CASE s.table_id
                WHEN 'T10101' THEN 'Real QoQ %'
                WHEN 'T10102' THEN 'Contribution to %Change'
                WHEN 'T10105' THEN 'Nominal (Billions USD)'
                WHEN 'T10106' THEN 'Real (Billions 2017 USD)'
            END                                AS "Type",
            CASE o.frequency
                WHEN 'Q' THEN 'Quarter'
                WHEN 'A' THEN 'Annual'
            END                                AS "Frequency",
            s.table_id                         AS "table_id"
        FROM nipa_observations o
        JOIN nipa_series s  ON s.id = o.series_id
        LEFT JOIN nipa_series ps
            ON ps.table_id = s.table_id
           AND ps.line     = s.parent_line
        ORDER BY s.table_id, s.depth, s.line, o.period
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df, df["Type"].unique(), df["Frequency"].unique(), df["table_id"].unique()

NAME_MAP = {
    "DFF":      "Fed Fund Rate",
    "DGS1MO":   "1-month",
    "DGS3MO":   "3-month",
    "DGS6MO":   "6-month",
    "DGS1":     "1-year",
    "DGS2":     "2-year",
    "DGS3":     "3-year",
    "DGS5":     "5-year",
    "DGS7":     "7-year",
    "DGS10":    "10-year",
    "DGS20":    "20-year",
    "DGS30":    "30-year",
    "DFII5":    "5-year",
    "DFII7":    "7-year",
    "DFII10":   "10-year",
    "DFII20":   "20-year",
    "DFII30":   "30-year",
    "DPRIME":   "Bank prime loan",
    "DPCREDIT": "Discount window primary credit",
}

@st.cache_data(ttl=3600)
def yield_data():
    conn = _get_db_conn()
    query = """
        SELECT o.date, m.fred_code, m.type, o.value
        FROM observations o
        JOIN series_meta m ON m.id = o.series_id
        WHERE m.category = 'yield_curve'
        ORDER BY o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["Name"]   = df["fred_code"].map(NAME_MAP)
    df["Values"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"]   = pd.to_datetime(df["date"])
    df = df.dropna(subset=["Values"])

    daily = df[["date", "Name", "type", "Values"]].copy()
    daily["Frequency"] = "Daily"
    daily["Date"] = daily["date"].dt.strftime("%Y-%m-%d")

    weekly_frames = []
    for (name, type_), grp in df.groupby(["Name", "type"]):
        wk = (grp.set_index("date")["Values"]
                 .resample("W-FRI").mean()
                 .dropna()
                 .reset_index())
        wk.columns = ["date", "Values"]
        wk["Name"]      = name
        wk["type"]      = type_
        wk["Frequency"] = "Weekly"
        wk["Date"]      = wk["date"].dt.strftime("%Y-%m-%d")
        weekly_frames.append(wk)
    weekly = pd.concat(weekly_frames, ignore_index=True)

    rates = pd.concat([
        daily[["Date", "Name", "Values", "Frequency", "type"]],
        weekly[["Date", "Name", "Values", "Frequency", "type"]],
    ], ignore_index=True).rename(columns={"type": "Type"})

    type_ = rates["Type"].unique()
    freq  = rates["Frequency"].unique()
    return type_, freq, rates

def _db_conn():
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
    return psycopg2.connect(
        host=os.environ["PGHOST"], user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"], port=int(os.environ["PGPORT"]),
        dbname=os.environ["PGDATABASE"], sslmode="require"
    )

def _fetch_prices(tickers):
    """Query daily market_prices for given tickers, return DataFrame with Ticker + OHLCV."""
    conn = _db_conn()
    sql = """
        SELECT date AS "Date", ticker AS "Ticker",
               adj_close AS "Adj Close", close AS "Close",
               high AS "High", low AS "Low",
               open AS "Open", volume AS "Volume"
        FROM market_prices
        WHERE ticker = ANY(%s)
        ORDER BY date
    """
    df = pd.read_sql(sql, conn, params=(tickers,))
    conn.close()
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def _resample_prices(df, rule):
    """Resample OHLCV per ticker to weekly (W-FRI) or monthly (ME) frequency."""
    parts = []
    for ticker, g in df.groupby('Ticker'):
        r = g.set_index('Date').resample(rule).agg({
            'Adj Close': 'last', 'Close': 'last',
            'High': 'max', 'Low': 'min',
            'Open': 'first', 'Volume': 'sum',
        }).dropna(subset=['Adj Close']).reset_index()
        r['Ticker'] = ticker
        parts.append(r)
    return pd.concat(parts, ignore_index=True) if parts else df.iloc[:0].copy()

def _format_dates(df):
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return df

@st.cache_data(ttl=3600)
def mkt_index_data():
    tickers = ['^GSPC', '^DJI', '^IXIC', '^NDX', '^RUT', '^VIX']
    daily   = _fetch_prices(tickers)
    weekly  = _resample_prices(daily, 'W-FRI')
    monthly = _resample_prices(daily, 'ME')
    return _format_dates(daily), _format_dates(weekly), _format_dates(monthly)

@st.cache_data(ttl=3600)
def sector_etf_data():
    tickers = ['XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY', 'XLRE', 'XLC']
    daily   = _fetch_prices(tickers)
    weekly  = _resample_prices(daily, 'W-FRI')
    monthly = _resample_prices(daily, 'ME')
    return _format_dates(daily), _format_dates(weekly), _format_dates(monthly)

@st.cache_data(ttl=3600)
def corp_oas_data():
    etf_tickers = ['HYG', 'JNK', 'LQD', 'SHY', 'TLT']
    daily   = _fetch_prices(etf_tickers)
    weekly  = _resample_prices(daily, 'W-FRI')
    monthly = _resample_prices(daily, 'ME')

    conn = _db_conn()
    oas = pd.read_sql("""
        SELECT date AS "Date", fred_code AS "Code",
               value AS "Values", name AS "Name", rating AS "Rating"
        FROM oas_spreads ORDER BY date, fred_code
    """, conn)
    conn.close()
    oas['Date'] = pd.to_datetime(oas['Date']).dt.strftime('%Y-%m-%d')

    return oas, _format_dates(daily), _format_dates(weekly), _format_dates(monthly)

@st.cache_data(ttl=3600)
def m2_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               m.name                         AS "Name",
               o.value                        AS "Values"
        FROM observations o
        JOIN series_meta m ON m.id = o.series_id
        WHERE m.category = 'm2'
        ORDER BY m.name, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=3600)
def pmi_data():
    """ISM Manufacturing PMI — independent DB query for PMI only."""
    import psycopg2, warnings
    from dotenv import load_dotenv
    warnings.filterwarnings("ignore", category=UserWarning)
    load_dotenv(os.path.join(BASE_DIR, '.env'))
    conn = psycopg2.connect(
        host=os.environ["PGHOST"], user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"], port=int(os.environ["PGPORT"]),
        dbname=os.environ["PGDATABASE"], sslmode="require"
    )

    level_df = pd.read_sql_query("""
        SELECT to_char(r.report_month, 'YYYY-MM-DD') AS "Date",
               l.sub_index, l.value
        FROM ism_level l
        JOIN ism_reports r ON r.id = l.report_id
        WHERE r.report_type = 'pmi'
        ORDER BY r.report_month, l.sub_index
    """, conn)
    index_data = level_df.pivot(index='Date', columns='sub_index', values='value').reset_index()
    index_data.columns.name = None

    glance_df = pd.read_sql_query("""
        SELECT mt.sub_index       AS "Index",
               l.value            AS "Current Value",
               mt.direction       AS "Direction",
               mt.rate_of_change  AS "Rate of Change",
               mt.trend_months    AS "Trend (Months)"
        FROM ism_monthly_table mt
        JOIN ism_reports r ON r.id = mt.report_id
        JOIN ism_level l   ON l.report_id = mt.report_id AND l.sub_index = mt.sub_index
        WHERE r.report_type = 'pmi'
          AND r.report_month = (
              SELECT MAX(r2.report_month) FROM ism_reports r2
              JOIN ism_monthly_table mt2 ON mt2.report_id = r2.id
              WHERE r2.report_type = 'pmi'
          )
        ORDER BY mt.sub_index
    """, conn)

    ranking_df = pd.read_sql_query("""
        SELECT to_char(r.report_month, 'YYYY-MM-DD') AS "Date",
               sr.sub_index   AS "Index",
               sr.industry    AS "Industry",
               sr.translation AS "Translation",
               sr.rank_value  AS "Rank"
        FROM ism_sector_ranking sr
        JOIN ism_reports r ON r.id = sr.report_id
        WHERE r.report_type = 'pmi'
        ORDER BY r.report_month DESC, sr.sub_index, sr.rank_value
    """, conn)
    if not ranking_df.empty:
        sector_ranking = ranking_df.pivot_table(
            index=['Index', 'Industry', 'Translation'],
            columns='Date', values='Rank'
        ).reset_index()
        sector_ranking.columns.name = None
    else:
        sector_ranking = ranking_df

    comments_df = pd.read_sql_query("""
        SELECT to_char(r.report_month, 'YYYY-MM-DD') AS "Date",
               c.industry     AS "Industry",
               c.comment_text AS "Comment"
        FROM ism_comments c
        JOIN ism_reports r ON r.id = c.report_id
        WHERE r.report_type = 'pmi'
        ORDER BY r.report_month DESC, c.industry
    """, conn)
    if not comments_df.empty:
        comments = comments_df.pivot_table(
            index='Industry', columns='Date', values='Comment', aggfunc='first'
        ).reset_index()
        comments.columns.name = None
    else:
        comments = comments_df

    conn.close()
    return comments, glance_df, index_data, sector_ranking


@st.cache_data(ttl=3600)
def nmi_data():
    """ISM Services NMI — independent DB query for NMI only."""
    import psycopg2, warnings
    from dotenv import load_dotenv
    warnings.filterwarnings("ignore", category=UserWarning)
    load_dotenv(os.path.join(BASE_DIR, '.env'))
    conn = psycopg2.connect(
        host=os.environ["PGHOST"], user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"], port=int(os.environ["PGPORT"]),
        dbname=os.environ["PGDATABASE"], sslmode="require"
    )

    level_df = pd.read_sql_query("""
        SELECT to_char(r.report_month, 'YYYY-MM-DD') AS "Date",
               l.sub_index, l.value
        FROM ism_level l
        JOIN ism_reports r ON r.id = l.report_id
        WHERE r.report_type = 'nmi'
        ORDER BY r.report_month, l.sub_index
    """, conn)
    index_data = level_df.pivot(index='Date', columns='sub_index', values='value').reset_index()
    index_data.columns.name = None

    glance_df = pd.read_sql_query("""
        SELECT mt.sub_index       AS "Index",
               l.value            AS "Current Value",
               mt.direction       AS "Direction",
               mt.rate_of_change  AS "Rate of Change",
               mt.trend_months    AS "Trend (Months)"
        FROM ism_monthly_table mt
        JOIN ism_reports r ON r.id = mt.report_id
        JOIN ism_level l   ON l.report_id = mt.report_id AND l.sub_index = mt.sub_index
        WHERE r.report_type = 'nmi'
          AND r.report_month = (
              SELECT MAX(r2.report_month) FROM ism_reports r2
              JOIN ism_monthly_table mt2 ON mt2.report_id = r2.id
              WHERE r2.report_type = 'nmi'
          )
        ORDER BY mt.sub_index
    """, conn)

    ranking_df = pd.read_sql_query("""
        SELECT to_char(r.report_month, 'YYYY-MM-DD') AS "Date",
               sr.sub_index   AS "Index",
               sr.industry    AS "Industry",
               sr.translation AS "Translation",
               sr.rank_value  AS "Rank"
        FROM ism_sector_ranking sr
        JOIN ism_reports r ON r.id = sr.report_id
        WHERE r.report_type = 'nmi'
        ORDER BY r.report_month DESC, sr.sub_index, sr.rank_value
    """, conn)
    if not ranking_df.empty:
        sector_ranking = ranking_df.pivot_table(
            index=['Index', 'Industry', 'Translation'],
            columns='Date', values='Rank'
        ).reset_index()
        sector_ranking.columns.name = None
    else:
        sector_ranking = ranking_df

    comments_df = pd.read_sql_query("""
        SELECT to_char(r.report_month, 'YYYY-MM-DD') AS "Date",
               c.industry     AS "Industry",
               c.comment_text AS "Comment"
        FROM ism_comments c
        JOIN ism_reports r ON r.id = c.report_id
        WHERE r.report_type = 'nmi'
        ORDER BY r.report_month DESC, c.industry
    """, conn)
    if not comments_df.empty:
        comments = comments_df.pivot_table(
            index='Industry', columns='Date', values='Comment', aggfunc='first'
        ).reset_index()
        comments.columns.name = None
    else:
        comments = comments_df

    conn.close()
    return comments, glance_df, index_data, sector_ranking

@st.cache_data(ttl=3600)
def umcsi_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(date, 'YYYY-MM-DD') AS "Date",
               series_name                 AS "Index",
               value                       AS "Values"
        FROM umcsi_observations
        ORDER BY series_name, date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=3600)
def housing_starts_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.name                        AS "Name",
               s.index_mapping               AS "Index Mapping"
        FROM hs_observations o
        JOIN hs_series s ON s.id = o.series_id
        ORDER BY s.index_mapping, s.name, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=3600)
def cpi_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.index_code                  AS "Index",
               s.name                        AS "Name",
               s.parent_name                 AS "Parent Name",
               s.parent_index                AS "Parent Index"
        FROM cpi_observations o
        JOIN cpi_series s ON s.id = o.series_id
        ORDER BY s.index_code, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Index"]        = df["Index"].astype(str)
    df["Parent Index"] = df["Parent Index"].fillna("").astype(str)
    return df

@st.cache_data(ttl=3600)
def ppi_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.index_level                 AS "Index Level",
               s.name                        AS "Name",
               s.parent_name                 AS "Parent Name",
               s.parent_index                AS "Parent Index"
        FROM ppi_observations o
        JOIN ppi_series s ON s.id = o.series_id
        ORDER BY s.index_level, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Index Level"]  = df["Index Level"].astype(str)
    df["Parent Index"] = df["Parent Index"].fillna("").astype(str)
    return df

@st.cache_data(ttl=3600)
def ip_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.index_level                 AS "Index Level",
               s.name                        AS "Name",
               s.category                    AS "Category",
               s.parent_name                 AS "Parent Name",
               s.parent_index                AS "Parent Index"
        FROM ip_observations o
        JOIN ip_series s ON s.id = o.series_id
        ORDER BY s.index_level, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Index Level"]  = df["Index Level"].astype(str)
    df["Parent Index"] = df["Parent Index"].fillna("").astype(str)
    return df

@st.cache_data(ttl=3600)
def cu_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.index_level                 AS "Index Level",
               s.name                        AS "Name",
               s.parent_name                 AS "Parent Name",
               s.parent_index                AS "Parent Index"
        FROM cu_observations o
        JOIN cu_series s ON s.id = o.series_id
        ORDER BY s.index_level, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Index Level"]  = df["Index Level"].astype(str)
    df["Parent Index"] = df["Parent Index"].fillna("").astype(str)
    return df

@st.cache_data(ttl=3600)
def business_inv_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.index_level                 AS "Index Level",
               s.name                        AS "Name",
               s.unit                        AS "Unit",
               s.parent_name                 AS "Parent Name",
               s.parent_index                AS "Parent Index"
        FROM business_observations o
        JOIN business_series s ON s.id = o.series_id
        ORDER BY s.index_level, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Index Level"]  = df["Index Level"].astype(str)
    df["Parent Index"] = df["Parent Index"].fillna("").astype(str)
    return df

@st.cache_data(ttl=3600)
def retail_sales_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.index_level                 AS "Index Level",
               s.name                        AS "Name",
               s.category                    AS "Category",
               s.parent_name                 AS "Parent Name",
               s.parent_index                AS "Parent Index"
        FROM retail_observations o
        JOIN retail_series s ON s.id = o.series_id
        ORDER BY s.index_level, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Index Level"]  = df["Index Level"].astype(str)
    df["Parent Index"] = df["Parent Index"].fillna("").astype(str)
    return df

@st.cache_data(ttl=3600)
def non_farm_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(o.date, 'YYYY-MM-DD') AS "Date",
               s.fred_code                   AS "Code",
               o.value                       AS "Values",
               s.index_level                 AS "Index",
               s.name                        AS "Name",
               s.parent_name                 AS "Parent Name",
               s.parent_index                AS "Parent Index"
        FROM employment_observations o
        JOIN employment_series s ON s.id = o.series_id
        ORDER BY s.index_level, o.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Index"]        = df["Index"].astype(str)
    df["Parent Index"] = df["Parent Index"].fillna("").astype(str)
    return df

@st.cache_data(ttl=3600)
def cot_report_data():
    conn = _get_db_conn()
    query = """
        SELECT to_char(report_date, 'YYYY-MM-DD') AS "Date",
               commodity                   AS "Commodity",
               commodity_group             AS "Group",
               open_interest               AS "Open Interest",
               mm_long                     AS "MM Long",
               mm_short                    AS "MM Short",
               net_pct_oi                  AS "Net % OI"
        FROM cot_data
        ORDER BY commodity, report_date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data


def line_chart(df):
    """Takes a pivoted dataframe (Date as index, series as columns) and returns a plotly line chart."""
    df_melted = df.reset_index().melt(id_vars='Date', var_name='Name', value_name='Values')
    fig = px.line(df_melted, x='Date', y='Values', color='Name')
    fig.add_hline(y=0, line_dash='solid', line_color='black')
    fig.update_layout(
        xaxis=dict(showgrid=True, nticks=10, linecolor='black', tickfont=dict(color='black'), title=''),
        yaxis=dict(tickformat='.2f', linecolor='black', tickfont=dict(color='black'), title=''),
        autosize=True,
        height=500
    )
    return fig


def create_bar_chart(df, x_col='Date', y_col='Values', color_col='Name', num_ticks=10, height=600):
    fig = px.bar(df, x=x_col, y=y_col, color=color_col)
    fig.add_hline(y=0, line_dash="solid", line_color="black")
    y_min, y_max = df[y_col].min(), df[y_col].max()
    tick_interval = (y_max - y_min) / num_ticks if y_max != y_min else 1
    tick_vals = np.arange(y_min, y_max + tick_interval, tick_interval)
    fig.update_layout(
        barmode='group',
        xaxis=dict(linecolor='black', tickfont=dict(color='black'), title='', linewidth=1, autorange=True, showgrid=True, nticks=10),
        yaxis=dict(tickvals=tick_vals, tickformat=".2f", linecolor='black', tickfont=dict(color='black'), title='', linewidth=2),
        autosize=True,
        height=height
    )
    return fig


def create_line_chart(df, x_col='Date', y_col='Values', color_col='Name', height=600):
    fig = px.line(df, x=x_col, y=y_col, color=color_col, render_mode='svg')
    fig.add_hline(y=0, line_dash="solid", line_color="black")
    fig.update_layout(
        xaxis=dict(linecolor='black', tickfont=dict(color='black'), title='', linewidth=1, autorange=True, showgrid=True, nticks=10),
        yaxis=dict(tickformat=".2f", linecolor='black', tickfont=dict(color='black'), title='', linewidth=2),
        autosize=True,
        height=height
    )
    return fig


def summary_statistics(df, key='stats'):
    """Display summary statistics for a dataframe. df should have Date + value columns (pivoted format)."""
    df_pivot = df.copy()
    if 'Name' in df_pivot.columns and 'Values' in df_pivot.columns:
        df_pivot = df_pivot.pivot_table(index='Date', columns='Name', values='Values')

    freq = st.radio("Select Frequency", ['MoM % Change', 'YoY % Change'], horizontal=True, key=f'freq_{key}')
    df_diff = df_pivot.copy()
    for col in df_diff.columns:
        if freq == 'MoM % Change':
            df_diff[col] = df_diff[col].pct_change()
        else:
            df_diff[col] = df_diff[col].pct_change(periods=12)

    stats = pd.concat([
        df_diff.mean(numeric_only=True).to_frame("Mean"),
        df_diff.sem(numeric_only=True).to_frame("Standard Error"),
        df_diff.median(numeric_only=True).to_frame("Median"),
        df_diff.mode(numeric_only=True).iloc[0].to_frame("Mode"),
        df_diff.std(numeric_only=True).to_frame("Standard Deviation"),
        df_diff.var(numeric_only=True).to_frame("Sample Variance"),
        df_diff.kurt(numeric_only=True).to_frame("Kurtosis"),
        df_diff.skew(numeric_only=True).to_frame("Skew"),
        (df_diff.max(numeric_only=True) - df_diff.min(numeric_only=True)).to_frame("Range"),
        df_diff.min(numeric_only=True).to_frame("Min"),
        df_diff.max(numeric_only=True).to_frame("Max"),
        df_diff.sum(numeric_only=True).to_frame("Sum"),
        df_diff.count(numeric_only=True).to_frame("Count"),
    ], axis=1)
    stats_table = stats.T.reset_index().rename(columns={'index': 'Descriptive Statistics'})
    st.dataframe(stats_table, hide_index=True, height=500)

    value_columns = [c for c in stats_table.columns if c != 'Descriptive Statistics']

    for std_mult, normal_pct in [(1, 0.6827), (2, 0.9545), (3, 0.9973)]:
        rows = []
        for col in value_columns:
            mean_val = float(stats_table.loc[stats_table['Descriptive Statistics'] == 'Mean', col].values[0])
            std_val = float(stats_table.loc[stats_table['Descriptive Statistics'] == 'Standard Deviation', col].values[0])
            total = float(stats_table.loc[stats_table['Descriptive Statistics'] == 'Count', col].values[0])
            vals = df_diff[col].dropna().values
            lo = round(mean_val - std_mult * std_val, 4)
            hi = round(mean_val + std_mult * std_val, 4)
            cnt = int(np.sum((vals >= lo) & (vals <= hi)))
            rows.append({f'{std_mult} STD Bounds': col, 'Lower': lo, 'Upper': hi,
                         'Actual Count': cnt, 'Actual %': f'{cnt/total:.2%}', 'Normal %': f'{normal_pct:.2%}'})
        st.dataframe(pd.DataFrame(rows), hide_index=True)

    for direction, label in [(1, 'Positive'), (-1, 'Negative'), (0, 'Zero')]:
        rows = []
        for col in value_columns:
            vals = df_diff[col].dropna().values
            total = len(vals)
            mask = vals > 0 if direction == 1 else (vals < 0 if direction == -1 else vals == 0)
            cnt = int(np.sum(mask))
            mean_chg = round(float(np.mean(mask)), 4)
            freq_pct = cnt / total if total > 0 else 0
            rows.append({f'{label} Return': col, 'Mean Change': mean_chg, 'Count': cnt,
                         'Frequency %': f'{freq_pct:.2%}', 'Prob Adj Change': round(mean_chg * freq_pct, 4)})
        st.dataframe(pd.DataFrame(rows), hide_index=True)

    pct_levels = [1, 2, 3, 4, 5, 10, 25, 50, 75, 90, 95, 96, 97, 98, 99]
    pct_df = pd.DataFrame({'Percentiles': [f'{p}%' for p in pct_levels]})
    for col in value_columns:
        pct_df[col] = np.nanpercentile(df_diff[col].dropna(), pct_levels)
    st.dataframe(pct_df, hide_index=True)

    select_columns = list(df_diff.columns)
    selection = st.radio("Select Series for Distribution", select_columns, horizontal=True, key=f'dist_{key}')
    if selection:
        distribution = df_diff[selection].dropna().values
        dis_mean, dis_std = np.mean(distribution), np.std(distribution)
        std_interval = [-3, -2.5, -2, -1.75, -1.5, -1.25, -1, -0.8, -0.6, -0.4, -0.2, 0,
                        0.2, 0.4, 0.6, 0.8, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, np.inf]
        bin_vals = [dis_mean + v * dis_std if v != np.inf else np.inf for v in std_interval]
        bin_labels = [round(dis_mean + v * dis_std, 4) if v != np.inf else 'More' for v in std_interval]
        dis_table = pd.DataFrame({'Interval': std_interval, 'Bin Value': bin_vals, 'Bin Label': bin_labels})
        bins = [-np.inf] + dis_table['Bin Value'].tolist()
        categories = pd.cut(distribution, bins=bins, labels=False, right=False, include_lowest=True)
        dis_table['Count'] = pd.Series(categories).value_counts().sort_index().values
        count_prob = dis_table['Count'] / len(distribution)
        cum_prob = count_prob.cumsum()
        dis_table['Probability'] = count_prob.apply(lambda x: f"{x*100:.2f}%")
        dis_table['Cum. Probability'] = cum_prob.apply(lambda x: f"{x*100:.2f}%")

        chart_table = dis_table.copy()
        chart_table['Prob_num'] = count_prob * 100
        fig = px.bar(chart_table, x='Bin Label', y='Prob_num',
                     title=f'{selection} Change Distribution',
                     labels={'Prob_num': 'Probability (%)', 'Bin Label': 'Range'},
                     text='Probability')
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(yaxis=dict(tickformat=".1f"), xaxis=dict(tickangle=-45))
        st.plotly_chart(fig)
        st.dataframe(dis_table, width='stretch', hide_index=True)


display_stats = summary_statistics
