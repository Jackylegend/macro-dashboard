import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from dataloader import non_farm_data, line_chart

# ── Data ────────────────────────────────────────────────────────────────────
nfp = non_farm_data()
# Standardise column name (dataloader returns 'Index' not 'Index Level')
if 'Index' in nfp.columns and 'Index Level' not in nfp.columns:
    nfp = nfp.rename(columns={'Index': 'Index Level'})

# ── Section 1: Top-level selector ────────────────────────────────────────────
depth1_levels = sorted(
    [lvl for lvl in nfp['Index Level'].unique() if '.' not in lvl],
    key=lambda x: int(x)
)
depth1_names = {lvl: nfp[nfp['Index Level'] == lvl]['Name'].iloc[0] for lvl in depth1_levels}

top_level = st.radio(
    "Select Category:",
    depth1_levels,
    format_func=lambda x: depth1_names.get(x, x),
    horizontal=True
)

# Depth-2 direct children
depth2_df = nfp[nfp['Parent Index'] == top_level]
depth2_levels = sorted(depth2_df['Index Level'].unique(), key=lambda x: [int(p) for p in x.split('.')])
depth2_names = {
    lvl: nfp[nfp['Index Level'] == lvl]['Name'].iloc[0]
    for lvl in depth2_levels
    if not nfp[nfp['Index Level'] == lvl].empty
}

if depth2_levels:
    sub_group = st.radio(
        "Select Sub-Group:",
        depth2_levels,
        format_func=lambda x: depth2_names.get(x, x),
        horizontal=True
    )
else:
    sub_group = top_level

# All series under top_level for snapshot bar chart
level_df = nfp[
    nfp['Index Level'].str.startswith(top_level + '.') |
    (nfp['Index Level'] == top_level)
][['Date', 'Name', 'Values']]

pivot = level_df.pivot_table(index='Date', columns='Name', values='Values').reset_index()

# ── Snapshot bar charts ──────────────────────────────────────────────────────
pct_mom = pivot.copy()
pct_yoy = pivot.copy()
for col in pivot.columns[1:]:
    pct_mom[col] = pct_mom[col].pct_change()
    pct_yoy[col] = pct_yoy[col].pct_change(periods=12)

latest = pivot['Date'].max()
snap_mom = pd.melt(pct_mom[pct_mom['Date'] == latest], id_vars='Date', var_name='Name', value_name='Values')
snap_yoy = pd.melt(pct_yoy[pct_yoy['Date'] == latest], id_vars='Date', var_name='Name', value_name='Values')
snap_mom['Values'] = snap_mom['Values'] * 100
snap_yoy['Values'] = snap_yoy['Values'] * 100
snap_mom = snap_mom.dropna().sort_values('Values')
snap_yoy = snap_yoy.dropna().sort_values('Values')

bar_height = max(400, len(snap_mom) * 22)

def make_bar(df, h):
    fig = px.bar(df, x='Values', y='Name', color='Name', height=h)
    fig.update_layout(
        xaxis=dict(linecolor='black', tickfont=dict(color='black'), title='%',
                   linewidth=1, autorange=True, showgrid=True, nticks=10),
        yaxis=dict(linecolor='black', tickfont=dict(color='black'), title='', linewidth=2),
        autosize=True, showlegend=False
    )
    fig.update_traces(texttemplate='%{x:.2f}%', textposition='outside', textfont=dict(color='black'))
    return fig

if len(snap_mom) > 1:
    tab1, tab2 = st.tabs(["YoY", "MoM"])
    with tab1:
        st.plotly_chart(make_bar(snap_yoy, bar_height), use_container_width=True)
    with tab2:
        st.plotly_chart(make_bar(snap_mom, bar_height), use_container_width=True)
else:
    # Single series (e.g. Unemployment Rate, Claims) — show line chart directly
    st.plotly_chart(line_chart(pivot.set_index('Date')), use_container_width=True, key='single_ts')

st.divider()

# ── Section 2: Sub-group series selector ─────────────────────────────────────
st.write("**Select series to plot over time**")

series_df = nfp[nfp['Parent Index'] == sub_group]
if series_df.empty:
    series_df = nfp[nfp['Index Level'] == sub_group]

all_names = sorted(series_df['Name'].unique().tolist())

if len(all_names) > 8:
    selected = st.multiselect('Select series:', all_names, default=all_names[:8])
elif len(all_names) > 0:
    selected = []
    cols = st.columns(max(len(all_names), 1))
    for i, name in enumerate(all_names):
        if cols[i].checkbox(name, value=(i == 0)):
            selected.append(name)
else:
    selected = []

if not selected:
    st.info("Please select at least one series.")
else:
    sel_df = series_df[series_df['Name'].isin(selected)][['Date', 'Name', 'Values']]
    sel_pivot = sel_df.pivot_table(index='Date', columns='Name', values='Values')

    mom = sel_pivot.copy()
    yoy = sel_pivot.copy()
    for col in sel_pivot.columns:
        mom[col] = sel_pivot[col].pct_change().round(4) * 100
        yoy[col] = sel_pivot[col].pct_change(periods=12).round(4) * 100

    tab3, tab4 = st.tabs(["📈 Chart", "🗃 Data"])
    with tab3:
        st.caption("Level (Thousands of persons)")
        st.plotly_chart(line_chart(sel_pivot), use_container_width=True, key='ts_level')
        st.caption("MoM % Change")
        st.plotly_chart(line_chart(mom), use_container_width=True, key='ts_mom')
        st.caption("YoY % Change")
        st.plotly_chart(line_chart(yoy), use_container_width=True, key='ts_yoy')
    with tab4:
        st.dataframe(sel_pivot.reset_index(), use_container_width=True)
        st.dataframe(mom.reset_index(), use_container_width=True)
        st.dataframe(yoy.reset_index(), use_container_width=True)

st.divider()

# ── Section 3: Descriptive Statistics ────────────────────────────────────────
st.write("**Descriptive Statistics**")
freq = st.radio("Select Frequency", ['MoM % Change', 'YoY % Change'], horizontal=True, key='stats_freq')

df_diff = pivot.set_index('Date').copy()
for col in df_diff.columns:
    df_diff[col] = df_diff[col].pct_change() if freq == 'MoM % Change' else df_diff[col].pct_change(periods=12)

mean_   = df_diff.mean(numeric_only=True).to_frame("Mean")
se_     = df_diff.sem(numeric_only=True).to_frame("Standard Error")
median_ = df_diff.median(numeric_only=True).to_frame("Median")
mode_r  = df_diff.mode(numeric_only=True)
mode_   = (mode_r.iloc[0] if not mode_r.empty else df_diff.mean(numeric_only=True)).to_frame("Mode")
std_    = df_diff.std(numeric_only=True).to_frame("Standard Deviation")
var_    = df_diff.var(numeric_only=True).to_frame("Sample Variance")
kurt_   = df_diff.kurt(numeric_only=True).to_frame("Kurtosis")
skew_   = df_diff.skew(numeric_only=True).to_frame("Skew")
range_  = (df_diff.max(numeric_only=True) - df_diff.min(numeric_only=True)).to_frame("Range")
min_    = df_diff.min(numeric_only=True).to_frame("Min")
max_    = df_diff.max(numeric_only=True).to_frame("Max")
sum_    = df_diff.sum(numeric_only=True).to_frame("Sum")
count_  = df_diff.count(numeric_only=True).to_frame("Count")

stats_table = pd.concat([mean_, se_, median_, mode_, std_, var_, kurt_, skew_, range_, min_, max_, sum_, count_], axis=1)
stats_table = stats_table.T.reset_index().rename(columns={'index': 'Descriptive Statistics'})
st.dataframe(stats_table, use_container_width=True)

st.divider()

# ── Section 4: STD Bounds + Probability Tables ───────────────────────────────
value_columns = [c for c in stats_table.columns if c != 'Descriptive Statistics']

std_bounce    = [{'Standard Deviation Bounds': lbl} for lbl in ['1 STD Lower Bound','1 STD Upper Bound','2 STD Lower Bound','2 STD Upper Bound','3 STD Lower Bound','3 STD Upper Bound','1 STD Actual Count','2 STD Actual Count','3 STD Actual Count','1 STD Actual %','2 STD Actual %','3 STD Actual %','1 STD Normal %','2 STD Normal %','3 STD Normal %']]
posi_prob_adj = [{'Positive Probability Adjusted Return': lbl} for lbl in ['Mean Change','Count','Frequency %','Prob Adj Change']]
nega_prob_adj = [{'Negative Probability Adjusted Return': lbl} for lbl in ['Mean Change','Count','Frequency %','Prob Adj Change']]
zero_prob_adj = [{'Zero Return': lbl} for lbl in ['Mean Change','Count','Frequency %','Prob Adj Change']]
percentiles_df = pd.DataFrame({'Percentiles': ['1%','2%','3%','4%','5%','10%','25%','50%','75%','90%','95%','96%','97%','98%','99%']})
pct_vals       = [1,2,3,4,5,10,25,50,75,90,95,96,97,98,99]

for col in value_columns:
    mean_v  = float(stats_table.loc[stats_table['Descriptive Statistics'] == 'Mean', col].values[0])
    std_v   = float(stats_table.loc[stats_table['Descriptive Statistics'] == 'Standard Deviation', col].values[0])
    total_n = float(stats_table.loc[stats_table['Descriptive Statistics'] == 'Count', col].values[0])
    vals    = df_diff[col].dropna().values
    for i, k in enumerate([1,2,3]):
        std_bounce[i*2][col]   = round(mean_v - k*std_v, 4)
        std_bounce[i*2+1][col] = round(mean_v + k*std_v, 4)
        cnt = int(np.sum((vals >= std_bounce[i*2][col]) & (vals <= std_bounce[i*2+1][col])))
        std_bounce[6+i][col] = cnt
        std_bounce[9+i][col] = f"{cnt/total_n:.2%}"
    std_bounce[12][col] = f"{0.6827:.2%}"; std_bounce[13][col] = f"{0.9545:.2%}"; std_bounce[14][col] = f"{0.9973:.2%}"
    pv = vals[vals>0]; posi_prob_adj[0][col]=round(float(np.mean(pv)) if len(pv) else 0,4); posi_prob_adj[1][col]=len(pv); posi_prob_adj[2][col]=f"{len(pv)/total_n:.2%}"; posi_prob_adj[3][col]=round(posi_prob_adj[0][col]*len(pv)/total_n,4)
    nv = vals[vals<0]; nega_prob_adj[0][col]=round(float(np.mean(nv)) if len(nv) else 0,4); nega_prob_adj[1][col]=len(nv); nega_prob_adj[2][col]=f"{len(nv)/total_n:.2%}"; nega_prob_adj[3][col]=round(nega_prob_adj[0][col]*len(nv)/total_n,4)
    zv = vals[vals==0]; zero_prob_adj[0][col]=round(float(np.mean(zv)) if len(zv) else 0,4); zero_prob_adj[1][col]=len(zv); zero_prob_adj[2][col]=f"{len(zv)/total_n:.2%}"; zero_prob_adj[3][col]=round(zero_prob_adj[0][col]*len(zv)/total_n,4)
    percentiles_df[col] = np.nanpercentile(vals, pct_vals)

st.dataframe(pd.DataFrame(std_bounce[0:2]+[std_bounce[6],std_bounce[9],std_bounce[12]]), use_container_width=True)
st.dataframe(pd.DataFrame(std_bounce[2:4]+[std_bounce[7],std_bounce[10],std_bounce[13]]), use_container_width=True)
st.dataframe(pd.DataFrame(std_bounce[4:6]+[std_bounce[8],std_bounce[11],std_bounce[14]]), use_container_width=True)
st.dataframe(pd.DataFrame(posi_prob_adj), use_container_width=True)
st.dataframe(pd.DataFrame(nega_prob_adj), use_container_width=True)
st.dataframe(pd.DataFrame(zero_prob_adj), use_container_width=True)
st.dataframe(percentiles_df, use_container_width=True)

st.divider()

# ── Section 5: Probability Distribution ──────────────────────────────────────
st.write("**Probability Distribution**")
dist_cols = [c for c in df_diff.columns]
if dist_cols:
    selection = st.radio("Select Series", dist_cols, horizontal=True)
    distribution = df_diff[selection].dropna().values
    if len(distribution) > 0:
        dis_mean = np.mean(distribution); dis_std = np.std(distribution)
        std_interval = [-3,-2.5,-2,-1.75,-1.5,-1.25,-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1,1.25,1.5,1.75,2,2.5,3,np.inf]
        bin_val   = [dis_mean+v*dis_std if v!=np.inf else np.inf for v in std_interval]
        bin_label = [round(dis_mean+v*dis_std,4) if v!=np.inf else 'More' for v in std_interval]
        dis_table = pd.DataFrame({'Interval':std_interval,'Bin Value':bin_val,'Bin Label':bin_label})
        try:
            bins = [-np.inf]+dis_table['Bin Value'].tolist()
            cat_result = pd.cut(distribution, bins=bins, labels=False, right=False, include_lowest=True)
            vc = pd.Series(cat_result).value_counts(); vc.index=vc.index.astype(int)
            value_counts = vc.reindex(np.arange(24), fill_value=0)
        except ValueError:
            value_counts = pd.Series(0, index=np.arange(24)); value_counts[11]=len(distribution)
        dis_table['Count'] = value_counts.values
        cp = dis_table['Count']/len(distribution); cum = cp.cumsum()
        dis_table['Probability'] = cp.apply(lambda x: f"{x*100:.2f}%")
        dis_table['Cum. Probability'] = cum.apply(lambda x: f"{x*100:.2f}%")
        dis_table['Prob_num'] = cp*100
        fig_dist = px.bar(dis_table, x='Bin Label', y='Prob_num', title=f'{selection} Change Distribution',
                          labels={'Prob_num':'Probability (%)','Bin Label':'Range'}, text='Probability')
        fig_dist.update_traces(texttemplate='%{text}', textposition='outside')
        fig_dist.update_layout(yaxis=dict(tickformat='.1f'), xaxis=dict(tickangle=-45))
        st.dataframe(dis_table[['Interval','Bin Label','Count','Probability','Cum. Probability']], use_container_width=True)
        st.plotly_chart(fig_dist, use_container_width=True)

st.divider()
