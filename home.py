import streamlit as st

# ── Placeholders — update these when ready ───────────────────────────────────
LINKEDIN_URL  = "https://www.linkedin.com/in/jackyziyanliu"
GITHUB_URL    = "https://github.com/Jackylegend/macro-dashboard"
EMAIL         = "fanj.liu@outlook.com"
BUYMEACOFFEE  = "https://buymeacoffee.com/jackylegend"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #1a73e8, #34a853);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-size: 1.1rem;
    color: #555;
    margin-bottom: 1.5rem;
}
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 3px 3px;
}
.badge-live   { background:#d4edda; color:#155724; }
.badge-wip    { background:#fff3cd; color:#856404; }
.badge-soon   { background:#f8d7da; color:#721c24; }
.card {
    background: #f8f9fa;
    border-left: 4px solid #1a73e8;
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.card h4 { margin: 0 0 4px 0; font-size: 1rem; color: #1a73e8; }
.card p  { margin: 0; font-size: 0.88rem; color: #444; line-height: 1.5; }
.card-inflation { border-left-color: #ea4335; }
.card-inflation h4 { color: #ea4335; }
.card-activity  { border-left-color: #34a853; }
.card-activity  h4 { color: #34a853; }
.card-consumer  { border-left-color: #fbbc04; }
.card-consumer  h4 { color: #b06a00; }
.card-employment{ border-left-color: #9c27b0; }
.card-employment h4 { color: #9c27b0; }
.contact-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 18px;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 600;
    text-decoration: none;
    margin: 4px 6px 4px 0;
    color: white !important;
}
.btn-linkedin { background: #0a66c2; }
.btn-github   { background: #24292e; }
.btn-email    { background: #34a853; }
.btn-coffee   { background: #ffdd00; color: #000 !important; }
.divider-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #888;
    text-transform: uppercase;
    margin: 1.5rem 0 0.6rem 0;
}
.about-box {
    background: linear-gradient(135deg, #eef4ff 0%, #f0fdf4 100%);
    border-radius: 10px;
    padding: 28px 32px;
    margin: 0.5rem 0 1rem 0;
}
.about-box h3 {
    margin: 0 0 12px 0;
    font-size: 1.25rem;
    color: #1a1a2e;
}
.about-box p {
    font-size: 0.95rem;
    color: #333;
    line-height: 1.75;
    margin-bottom: 14px;
}
.about-box p:last-child { margin-bottom: 0; }
.flow-chain {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    margin: 16px 0;
    font-size: 0.88rem;
}
.flow-node {
    background: #1a73e8;
    color: white;
    border-radius: 20px;
    padding: 5px 14px;
    font-weight: 600;
    white-space: nowrap;
}
.flow-arrow {
    color: #888;
    font-size: 1.1rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ── About Me ──────────────────────────────────────────────────────────────────
st.markdown("## 👤 About Me & This Project")
st.markdown("""
<div class="about-box">
    <h3>Hi — My name is Jacky and I am a financial professional working on Wall Street Investment Bank.</h3>
    <p>
        This dashboard is a side project that reflects a core part of how I think about markets:
        <strong>top-down macro analysis</strong>.
        Before sizing a position or forming a sector view, I start with the
        macro landscape — and this app is my personal tool for doing exactly that.
    </p>
    <p><strong>Why macro first?</strong></p>
    <div class="flow-chain">
        <span class="flow-node">📊 Macro Conditions</span>
        <span class="flow-arrow">→</span>
        <span class="flow-node">🏭 Corporate Investment &amp; Profits</span>
        <span class="flow-arrow">→</span>
        <span class="flow-node">🛍️ Consumer Spending</span>
        <span class="flow-arrow">→</span>
        <span class="flow-node">📈 Equity Market Returns</span>
    </div>
    <p>
        Macro conditions set the playing field. Interest rates, inflation, employment,
        and output growth determine the environment in which companies operate,
        consumers spend, and investors price risk. Getting the macro call right —
        or at least understanding the macro backdrop — is the foundation of any
        durable investment thesis.
    </p>
    <p>
        This dashboard aggregates the economic indicators I track most closely,
        with an emphasis on <strong>leading indicators</strong> that tend to
        signal turning points <em>before</em> they show up in earnings or
        price action. The list is always growing — I add new data series as my
        research evolves, so check back regularly.
    </p>
    <p style="color:#888; font-size:0.85rem;">
        Have a question about the data, a suggestion, or just want to connect?
        Reach out anytime via the contact links at the bottom of this page.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">📊 US Macro Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">This is a personal macroeconomic dashboard project focused on tracking key U.S. economic indicators. Data is updated weekly using official sources, including the Federal Reserve, Bureau of Labor Statistics, Census Bureau, ISM, and other public APIs. The project will continue to expand over time with the aim of building a more comprehensive view of the U.S. economy, and eventually, broader global macro coverage. Because development time is limited, new datasets are added on a best-effort basis. If there is a macroeconomic indicator you care about most, send me a suggestion and I will prioritize it.</p>',
    unsafe_allow_html=True
)

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Indicators Tracked", "20+")
with col_b:
    st.metric("Data Update Cadence", "Weekly")
with col_c:
    st.metric("Data Source", "FRED / BLS / Census / ISM")

st.divider()

# ── What's Inside ─────────────────────────────────────────────────────────────
st.markdown("## 📂 What's Inside")
st.markdown(
    "Each section of this dashboard covers a different lens on the US economy. "
    "Use the sidebar to navigate between pages."
)

# ── Markets ───────────────────────────────────────────────────────────────────
st.markdown('<p class="divider-label">Markets</p>', unsafe_allow_html=True)
cols = st.columns(2)
indicators_markets = [
    ("📈 US GDP", "markets",
     "Gross Domestic Product measures the total economic output of the US. "
     "It's the broadest scorecard of the economy — tracking whether growth is accelerating, "
     "decelerating, or contracting, and decomposing the drivers (consumption, investment, government, trade)."),
    ("📉 Yield Curve", "markets",
     "The yield curve plots US Treasury yields across maturities. An inverted curve (short rates > long rates) "
     "has historically preceded recessions. This page tracks the spread dynamics and curve shape over time."),
    ("🏦 Corp OAS & ETFs", "markets",
     "Option-Adjusted Spreads on corporate bonds reflect credit risk appetite. Widening spreads signal stress; "
     "tightening spreads signal risk-on conditions. Paired with ETF flows for a full credit market picture."),
    ("📊 Market Index", "markets",
     "Tracks major equity indices (S&P 500, Nasdaq, Dow Jones, Russell 2000). "
     "Useful for understanding risk sentiment and sector rotation in the context of macro releases."),
    ("🥧 Sector ETFs", "markets",
     "Sector ETF performance reveals which parts of the economy the market is pricing for strength or weakness — "
     "a real-time read on cyclical vs. defensive positioning."),
    ("💵 M2 Money Supply", "markets",
     "M2 measures the total amount of money circulating in the economy. "
     "Rapid M2 growth can be inflationary; contraction can signal tightening financial conditions."),
]
for i, (title, cat, desc) in enumerate(indicators_markets):
    with cols[i % 2]:
        st.markdown(f'<div class="card"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ── Inflation ─────────────────────────────────────────────────────────────────
st.markdown('<p class="divider-label">Inflation</p>', unsafe_allow_html=True)
cols2 = st.columns(2)
indicators_inflation = [
    ("🛒 CPI — Consumer Price Index", "inflation",
     "The Fed's most-watched inflation gauge. CPI tracks price changes for a basket of consumer goods and services. "
     "Core CPI (ex food & energy) is the key measure for monetary policy. This page drills into parent and sub-categories."),
    ("🏭 PPI — Producer Price Index", "inflation",
     "PPI measures inflation at the wholesale/producer level — often a leading indicator for CPI. "
     "Rising input costs flow through supply chains and eventually reach consumers."),
]
for i, (title, cat, desc) in enumerate(indicators_inflation):
    with cols2[i % 2]:
        st.markdown(f'<div class="card card-inflation"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ── Activity ──────────────────────────────────────────────────────────────────
st.markdown('<p class="divider-label">Economic Activity</p>', unsafe_allow_html=True)
cols3 = st.columns(2)
indicators_activity = [
    ("🏭 ISM PMI — Manufacturing", "activity",
     "The ISM Purchasing Managers' Index surveys manufacturing firms on orders, production, employment, and prices. "
     "A reading above 50 signals expansion. Sub-indices like New Orders and Backlogs are key leading indicators."),
    ("🏪 ISM NMI — Services", "activity",
     "The non-manufacturing equivalent of the PMI, covering the 80%+ of the economy that is services. "
     "The Business Activity and New Orders sub-indices are particularly informative about service sector momentum."),
    ("⚙️ Industrial Production", "activity",
     "Monthly Fed measure of output from manufacturing, mining, and utilities — a real-time gauge of the goods-producing "
     "economy. Drilling into Market Group vs Industry Group reveals which sectors are leading or lagging."),
    ("🔋 Capacity Utilization", "activity",
     "Measures what percentage of productive capacity is being used. High utilization (>80%) signals inflationary "
     "pressure and investment demand; low utilization signals slack in the economy."),
    ("📦 Durable Goods & Shipments", "activity",
     "Orders for long-lived manufactured goods (aircraft, machinery, computers). "
     "Core capital goods orders (ex-defense, ex-aircraft) are a reliable leading indicator of business investment. "
     "⚠️ *This page is under construction.*"),
    ("🏠 Housing Starts", "activity",
     "Tracks new residential construction. Housing is highly interest-rate sensitive and leads the broader economy. "
     "Building permits are an even earlier leading indicator of construction activity."),
]
for i, (title, cat, desc) in enumerate(indicators_activity):
    with cols3[i % 2]:
        st.markdown(f'<div class="card card-activity"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ── Consumer ──────────────────────────────────────────────────────────────────
st.markdown('<p class="divider-label">Consumer</p>', unsafe_allow_html=True)
cols4 = st.columns(2)
indicators_consumer = [
    ("😊 UMich Consumer Sentiment", "consumer",
     "University of Michigan's monthly survey of consumer confidence. Tracks current conditions and expectations "
     "separately. Sentiment is a leading indicator — pessimistic consumers tend to pull back spending before it shows in hard data."),
    ("🛍️ Retail Sales", "consumer",
     "Monthly Census Bureau measure of consumer spending at the register. Ex-auto and ex-gasoline core retail is "
     "the cleanest read on underlying consumer demand and feeds directly into GDP."),
    ("🏬 Business Sales & Inventory", "consumer",
     "Tracks total business sales, inventories, and the inventory-to-sales ratio across manufacturers, retailers, "
     "and wholesalers. An elevated I/S ratio signals potential future production cuts."),
]
for i, (title, cat, desc) in enumerate(indicators_consumer):
    with cols4[i % 2]:
        st.markdown(f'<div class="card card-consumer"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ── Employment ────────────────────────────────────────────────────────────────
st.markdown('<p class="divider-label">Employment</p>', unsafe_allow_html=True)
cols5 = st.columns(2)
indicators_employment = [
    ("👷 Non-Farm Payrolls", "employment",
     "The BLS CES report — the most market-moving monthly data release. Tracks job creation across all private and "
     "government sectors. The unemployment rate and average hourly earnings (wage inflation) complete the picture."),
    ("📋 Jobless Claims", "employment",
     "Weekly initial and continued unemployment insurance claims. The highest-frequency labor market signal available. "
     "Spikes in initial claims are an early warning of labor market deterioration."),
]
for i, (title, cat, desc) in enumerate(indicators_employment):
    with cols5[i % 2]:
        st.markdown(f'<div class="card card-employment"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

st.divider()

# ── Status & Disclaimer ───────────────────────────────────────────────────────
st.markdown("## ℹ️ Status & Disclaimer")

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown("""
**🟢 Live pages** — data fully functional:
- GDP, Yield Curve, Corp OAS & ETFs
- Market Index, Sector ETFs, M2 Money Supply
- CPI, PPI
- ISM PMI, ISM NMI
- Industrial Production, Capacity Utilization
- Business Sales & Inventory
- Housing Starts, UMich Consumer Sentiment
- Non-Farm Payrolls, Jobless Claims, Retail Sales
""")
with col_s2:
    st.markdown("""
**🟡 Under Construction** — coming soon:
- COT Report & Dollar Index *(data ingestion pending)*
- Durable Goods & Shipments *(data ingestion pending)*

**📅 Update Cadence**
Data is pulled from the database and refreshed on a **weekly basis**, roughly aligned with official release schedules.

**⚠️ Disclaimer**
This is a personal project for educational and analytical purposes. It is not financial advice.
""")

st.divider()

# ── Contact & Open Source ─────────────────────────────────────────────────────
st.markdown("## 🤝 Contact & Open Source")
st.markdown(
    "Have a bug report, feature request, or question? Feel free to reach out or open an issue on GitHub. "
    "This project is open source — clone it, fork it, adapt it for your own macro research."
)

st.markdown(f"""
<a class="contact-btn btn-linkedin" href="{LINKEDIN_URL}" target="_blank">
    🔗 LinkedIn
</a>
<a class="contact-btn btn-github" href="{GITHUB_URL}" target="_blank">
    🐙 GitHub / Clone
</a>
<a class="contact-btn btn-email" href="mailto:{EMAIL}">
    ✉️ Email Me
</a>
<a class="contact-btn btn-coffee" href="{BUYMEACOFFEE}" target="_blank">
    ☕ Buy Me a Coffee
</a>
""", unsafe_allow_html=True)

st.markdown("")
st.caption(
    "If you find this dashboard useful, a coffee is always appreciated — but never expected. "
    "The goal is to make macro data more accessible to everyone."
)