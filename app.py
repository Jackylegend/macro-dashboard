import streamlit as st

st.set_page_config(page_title="Macro Dashboard", page_icon=":material/bar_chart:", layout='wide')

home         = st.Page("home.py",                       title="Home",                             icon=":material/home:")
gdp          = st.Page("pages/gdp.py",                  title="US GDP",                           icon=":material/trending_up:")
rates        = st.Page("pages/rates.py",                title="Yield Curve",                      icon=":material/show_chart:")
corp_oas     = st.Page("pages/corp_oas_etfs.py",        title="Corp OAS and ETFs",                icon=":material/account_balance:")
market_index = st.Page("pages/market_index.py",         title="Market Index",                     icon=":material/candlestick_chart:")
sector_etf   = st.Page("pages/sector_etf.py",           title="Sector ETFs",                      icon=":material/pie_chart:")
m2           = st.Page("pages/m2.py",                   title="M2 Money Supply",                  icon=":material/payments:")
pmi          = st.Page("pages/ism_pmi.py",              title="ISM PMI",                          icon=":material/factory:")
nmi          = st.Page("pages/ism_nmi.py",              title="ISM NMI",                          icon=":material/store:")
umcsi        = st.Page("pages/umcsi.py",                title="UMich Consumer Sentiment",         icon=":material/sentiment_satisfied:")
housing      = st.Page("pages/housing_starts.py",       title="Housing Starts",                   icon=":material/home_work:")
cot          = st.Page("pages/cot_report.py",           title="COT Report and Dollar Index",      icon=":material/currency_exchange:")
cpi          = st.Page("pages/cpi.py",                  title="CPI",                              icon=":material/shopping_cart:")
ppi          = st.Page("pages/ppi.py",                  title="PPI",                              icon=":material/precision_manufacturing:")
ip           = st.Page("pages/ip.py",                   title="Industrial Production",            icon=":material/settings:")
cu           = st.Page("pages/cu.py",                   title="Capacity Utilization",             icon=":material/speed:")
durables     = st.Page("pages/durable_goods.py",        title="Durable Goods and Shipments",      icon=":material/inventory:")
business     = st.Page("pages/business_sales_inv.py",   title="Business Sales and Inventory",     icon=":material/storefront:")
retail       = st.Page("pages/retail_sales.py",         title="Retail Sales",                     icon=":material/shopping_bag:")
non_farm     = st.Page("pages/non_farm.py",             title="Non-Farm Payrolls",                icon=":material/people:")
jobless      = st.Page("pages/jobless_claims.py",       title="Jobless Claims",                   icon=":material/work_off:")

pages = {
    " ": [home],
    "Markets": [gdp, rates, corp_oas, market_index, sector_etf, m2, cot],
    "Inflation": [cpi, ppi],
    "Activity": [pmi, nmi, ip, cu, durables, housing],
    "Consumer": [umcsi, retail, business],
    "Employment": [non_farm, jobless],
}

pg = st.navigation(pages)
pg.run()
