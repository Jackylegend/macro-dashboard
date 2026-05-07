import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from dataloader import load_gdp_data

gdp_data, type_, freq, _ = load_gdp_data()

# ── Filters ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    selected_type = st.radio('Select Type', type_, horizontal=True)
with col2:
    selected_freq = st.radio('Select Frequency', freq, horizontal=True)

filtered_df = gdp_data[
    (gdp_data['Type'] == selected_type) &
    (gdp_data['Frequency'] == selected_freq)
]

# ── Snapshot: latest period horizontal bar chart ───────────────────────────────
snap_all = filtered_df[
    ((filtered_df['depth'] == 0) & (filtered_df['line'] == 1)) |
    (filtered_df['depth'] >= 1)
][['Date', 'Name', 'Values', 'depth', 'parent_name']].copy()
snap_all['Values'] = pd.to_numeric(snap_all['Values'], errors='coerce')

if not snap_all.empty:
    max_depth = int(snap_all['depth'].max())
    depth_options = {f'Level {d}': d for d in range(1, max_depth + 1)}
    depth_options['All Levels'] = None

    sc1, sc2 = st.columns([3, 1])
    with sc2:
        depth_choice = st.selectbox('Show depth', list(depth_options.keys()), key='snap_depth')
    selected_depth = depth_options[depth_choice]

    if selected_depth is None:
        snap_df = snap_all.copy()
    else:
        snap_df = snap_all[
            (snap_all['depth'] == 0) | (snap_all['depth'] == selected_depth)
        ].copy()

    # disambiguate duplicate names by prefixing with parent name
    dup_names = snap_df['Name'][snap_df['Name'].duplicated(keep=False)]
    snap_df['Label'] = snap_df.apply(
        lambda r: f"{r['parent_name']}: {r['Name']}" if r['Name'] in dup_names.values and pd.notna(r['parent_name']) else r['Name'],
        axis=1
    )

    latest = snap_df['Date'].max()
    is_level = selected_type in ('Nominal (Billions USD)', 'Real (Billions 2017 USD)')

    if is_level:
        periods = 4 if selected_freq == 'Quarter' else 1
        pivot = snap_df.pivot_table(index='Date', columns='Label', values='Values').sort_index()
        pct = pivot.pct_change(periods=periods) * 100
        snap_latest = pct.loc[pct.index.max()].dropna().reset_index()
        snap_latest.columns = ['Label', 'Values']
        change_label = 'QoQ % Change' if selected_freq == 'Quarter' else 'YoY % Change'
        title_suffix = f' ({change_label}, {latest})'
    else:
        snap_latest = snap_df[snap_df['Date'] == latest][['Label', 'Values']].dropna()
        title_suffix = f' ({latest})'

    snap_latest = snap_latest.sort_values('Values')
    chart_height = max(400, len(snap_latest) * 30)

    fig_snap = px.bar(
        snap_latest, x='Values', y='Label', color='Label', orientation='h',
        title=f'GDP Components — {selected_type}{title_suffix}',
        labels={'Values': selected_type, 'Label': ''},
    )
    fig_snap.add_vline(x=0, line_dash='solid', line_color='black')
    fig_snap.update_traces(texttemplate='%{x:.2f}', textposition='outside')
    fig_snap.update_layout(
        showlegend=False, height=chart_height,
        xaxis=dict(linecolor='black', showgrid=True, tickformat='.2f'),
        yaxis=dict(linecolor='black'),
    )
    st.plotly_chart(fig_snap, use_container_width=True)

st.divider()

# ── Summary statistics (unchanged from original) ───────────────────────────────
def summary_statistics(df, key='header'):
    if df.empty:
        st.info('No data selected.')
        return
    df_diff = df.copy()
    df_diff['Values'] = pd.to_numeric(df_diff['Values'], errors='coerce')
    df_diff = df_diff.pivot_table(index='Date', columns='Name', values='Values')

    mean         = df_diff.mean(numeric_only=True).to_frame("Mean")
    stand_error  = df_diff.sem(numeric_only=True).to_frame("Standard Error")
    median       = df_diff.median(numeric_only=True).to_frame("Median")
    mode_result  = df_diff.mode(numeric_only=True)
    mode         = (mode_result.iloc[0] if not mode_result.empty else df_diff.mean(numeric_only=True)).to_frame("Mode")
    std          = df_diff.std(numeric_only=True).to_frame("Standard Deviation")
    s_var        = df_diff.var(numeric_only=True).to_frame("Sample Variance")
    kurt         = df_diff.kurt(numeric_only=True).to_frame("Kurtosis")
    skew         = df_diff.skew(numeric_only=True).to_frame("Skew")
    rng          = (df_diff.max(numeric_only=True) - df_diff.min(numeric_only=True)).to_frame("Range")
    mn           = df_diff.min(numeric_only=True).to_frame("Min")
    mx           = df_diff.max(numeric_only=True).to_frame("Max")
    sm           = df_diff.sum(numeric_only=True).to_frame("Sum")
    cnt          = df_diff.count(numeric_only=True).to_frame("Count")

    stats_table  = pd.concat([mean, stand_error, median, mode, std, s_var, kurt, skew, rng, mn, mx, sm, cnt], axis=1)
    stats_table  = stats_table.T.reset_index().rename(columns={'index': 'Descriptive Statistics'})
    value_columns = [c for c in stats_table.columns if c != 'Descriptive Statistics']

    std_bounce   = [{'Standard Deviation Bounds': lbl} for lbl in [
        '1 STD Lower','1 STD Upper','2 STD Lower','2 STD Upper','3 STD Lower','3 STD Upper',
        '1 STD Count','2 STD Count','3 STD Count','1 STD %','2 STD %','3 STD %',
        '1 STD Normal %','2 STD Normal %','3 STD Normal %']]
    posi_prob_adj = [{'Positive Prob Adj Return': l} for l in ['Mean Change','Count','Frequency %','Prob Adj Change']]
    nega_prob_adj = [{'Negative Prob Adj Return': l} for l in ['Mean Change','Count','Frequency %','Prob Adj Change']]
    zero_prob_adj = [{'Zero Return':              l} for l in ['Mean Change','Count','Frequency %','Prob Adj Change']]
    pct_levels    = [1,2,3,4,5,10,25,50,75,90,95,96,97,98,99]
    percentiles_df = pd.DataFrame({'Percentiles': [f'{p}%' for p in pct_levels]})

    for col in value_columns:
        mean_val  = float(stats_table.loc[stats_table['Descriptive Statistics']=='Mean', col].values[0])
        std_val   = float(stats_table.loc[stats_table['Descriptive Statistics']=='Standard Deviation', col].values[0])
        total     = float(stats_table.loc[stats_table['Descriptive Statistics']=='Count', col].values[0])
        vals      = df_diff[col].dropna().values
        for i, m in enumerate([1, 2, 3]):
            lo = round(mean_val - m*std_val, 4); hi = round(mean_val + m*std_val, 4)
            std_bounce[i*2][col]   = lo; std_bounce[i*2+1][col] = hi
            cnt_in = int(np.sum((vals >= lo) & (vals <= hi)))
            std_bounce[6+i][col]   = cnt_in
            std_bounce[9+i][col]   = f'{cnt_in/total:.2%}'
            std_bounce[12+i][col]  = f'{[0.6827,0.9545,0.9973][i]:.2%}'
        for prob_list, mask in [
            (posi_prob_adj, vals > 0),
            (nega_prob_adj, vals < 0),
            (zero_prob_adj, vals == 0)]:
            c = int(np.sum(mask)); fp = c/total if total else 0
            m = round(float(np.mean(mask)), 4)
            prob_list[0][col]=m; prob_list[1][col]=c
            prob_list[2][col]=f'{fp:.2%}'; prob_list[3][col]=round(m*fp,4)
        percentiles_df[col] = np.nanpercentile(df_diff[col].dropna(), pct_levels)

    std1 = pd.DataFrame([std_bounce[0],std_bounce[1],std_bounce[6],std_bounce[9],std_bounce[12]])
    std2 = pd.DataFrame([std_bounce[2],std_bounce[3],std_bounce[7],std_bounce[10],std_bounce[13]])
    std3 = pd.DataFrame([std_bounce[4],std_bounce[5],std_bounce[8],std_bounce[11],std_bounce[14]])
    posi = pd.DataFrame(posi_prob_adj); nega = pd.DataFrame(nega_prob_adj); zero = pd.DataFrame(zero_prob_adj)

    select_columns = list(df_diff.columns)
    selection = st.radio("Data Type", select_columns, horizontal=True, key=key)
    if selection:
        distribution = df_diff[selection].dropna().values
        dis_mean, dis_std = np.mean(distribution), np.std(distribution)
        std_interval = [-3,-2.5,-2,-1.75,-1.5,-1.25,-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1,1.25,1.5,1.75,2,2.5,3,np.inf]
        bin_val   = [dis_mean+v*dis_std if v!=np.inf else np.inf for v in std_interval]
        bin_label = [round(dis_mean+v*dis_std,4) if v!=np.inf else 'More' for v in std_interval]
        dis_table = pd.DataFrame({'Interval':std_interval,'Bin Value':bin_val,'Bin Label':bin_label})
        try:
            bins = [-np.inf]+dis_table['Bin Value'].tolist()
            cat  = pd.cut(distribution,bins=bins,labels=False,right=False,include_lowest=True)
            vc   = pd.Series(cat).value_counts().reindex(np.arange(24),fill_value=0)
        except ValueError:
            vc = pd.Series(0,index=np.arange(24)); vc[11]=len(distribution)
        dis_table['Count'] = vc.values
        count_prob = dis_table['Count']/len(distribution)
        dis_table['Probability']     = count_prob.apply(lambda x: f'{x*100:.2f}%')
        dis_table['Cum. Probability']= count_prob.cumsum().apply(lambda x: f'{x*100:.2f}%')
        chart_table = dis_table.copy(); chart_table['Prob_num'] = count_prob*100
        fig = px.bar(chart_table,x='Bin Label',y='Prob_num',title=f'{selection} Distribution',
                     labels={'Prob_num':'Probability (%)','Bin Label':'Range'},text='Probability')
        fig.update_traces(texttemplate='%{text}',textposition='outside')
        fig.update_layout(yaxis=dict(tickformat='.1f'),xaxis=dict(tickangle=-45))
        st.plotly_chart(fig)
        st.dataframe(dis_table,width='stretch',hide_index=True,height=900)
    st.dataframe(stats_table,hide_index=True,height=500)
    st.dataframe(std1,hide_index=True,height=230)
    st.dataframe(std2,hide_index=True,height=230)
    st.dataframe(std3,hide_index=True,height=230)
    st.dataframe(posi,hide_index=True,height=200)
    st.dataframe(nega,hide_index=True,height=200)
    st.dataframe(zero,hide_index=True,height=200)
    st.dataframe(percentiles_df,hide_index=True,height=580)

# ── Helper: bar + line charts ──────────────────────────────────────────────────
def make_charts(chart_df):
    if chart_df.empty:
        return None, None
    y_min, y_max = chart_df['Values'].min(), chart_df['Values'].max()
    tick_interval = (y_max-y_min)/10 if y_max!=y_min else 1
    tick_vals = np.arange(y_min, y_max+tick_interval, tick_interval)
    layout = dict(xaxis=dict(linecolor='black',tickfont=dict(color='black'),title='',
                             linewidth=1,autorange=True,showgrid=True,nticks=10),
                  yaxis=dict(tickvals=tick_vals,tickformat='.2f',linecolor='black',
                             tickfont=dict(color='black'),title='',linewidth=2),
                  autosize=True,height=600)
    fig_bar = px.bar(chart_df,x='Date',y='Values',color='Name')
    fig_bar.add_hline(y=0,line_dash='solid',line_color='black')
    fig_bar.update_layout(barmode='group',**layout)
    fig_line = px.line(chart_df,x='Date',y='Values',color='Name')
    fig_line.add_hline(y=0,line_dash='solid',line_color='black')
    fig_line.update_layout(**layout)
    return fig_bar, fig_line

def show_section(chart_df, pivot_df, key_suffix):
    fig_bar, fig_line = make_charts(chart_df)
    t1, t2, t3, t4 = st.tabs(['📈 Line Chart', '📊 Bar Chart', '🗃 Data Table', '🗃 Summary Statistics'])
    with t1:
        if fig_line:
            st.plotly_chart(fig_line)
        else:
            st.info('No data')
    with t2:
        if fig_bar:
            st.plotly_chart(fig_bar)
        else:
            st.info('No data')
    with t3:
        st.dataframe(pivot_df, width='stretch')
    with t4:
        summary_statistics(chart_df, key=key_suffix)

# ── Level 1: GDP + direct components (depth 0 line 1, and depth 1) ─────────────
level1_df = filtered_df[
    ((filtered_df['depth'] == 0) & (filtered_df['line'] == 1)) |
    (filtered_df['depth'] == 1)
][['Date','Name','Values']].copy()

column_names = level1_df['Name'].unique()
st.write('**Select Level 1 components:**')
if len(column_names) == 0:
    st.info('No data for this selection.')
    st.stop()
cols = st.columns(len(column_names))
selected_names = [n for i,n in enumerate(column_names) if cols[i].checkbox(n)]

level1_chart = level1_df[level1_df['Name'].isin(selected_names)]
level1_pivot = level1_chart.pivot_table(index='Date',columns='Name',values='Values')
show_section(level1_chart, level1_pivot, 'l1')

st.divider()

# ── Level 2: children of depth-1 items ────────────────────────────────────────
st.write('**Select a Level 1 component to drill into Level 2:**')
depth1_lines = filtered_df[filtered_df['depth']==1]['line'].unique().tolist()
level2 = filtered_df[filtered_df['parent_line'].isin(depth1_lines)]

if not level2.empty:
    parent_opts = level2[['parent_line','parent_name']].drop_duplicates()
    parent_map  = dict(zip(parent_opts['parent_line'].astype(str), parent_opts['parent_name']))
    sel2 = st.selectbox('Select Parent (Level 1)', options=list(parent_map.keys()),
                        format_func=lambda x: parent_map[x], key='sel2')
    level2_chart = level2[level2['parent_line'].astype(str)==sel2][['Date','Name','Values']]
    level2_pivot = level2_chart.pivot_table(index='Date',columns='Name',values='Values')
    show_section(level2_chart, level2_pivot, 'l2')
else:
    st.info('No Level 2 data for this selection.')

st.divider()

# ── Level 3: children of depth-2 items ────────────────────────────────────────
st.write('**Select a Level 2 component to drill into Level 3:**')
depth2_lines = filtered_df[filtered_df['depth']==2]['line'].unique().tolist()
level3 = filtered_df[filtered_df['parent_line'].isin(depth2_lines)]

if not level3.empty:
    parent_opts = level3[['parent_line','parent_name']].drop_duplicates()
    parent_map  = dict(zip(parent_opts['parent_line'].astype(str), parent_opts['parent_name']))
    sel3 = st.selectbox('Select Parent (Level 2)', options=list(parent_map.keys()),
                        format_func=lambda x: parent_map[x], key='sel3')
    level3_chart = level3[level3['parent_line'].astype(str)==sel3][['Date','Name','Values']]
    level3_pivot = level3_chart.pivot_table(index='Date',columns='Name',values='Values')
    show_section(level3_chart, level3_pivot, 'l3')
else:
    st.info('No Level 3 data for this selection.')

st.divider()

# ── Level 4: children of depth-3 items ────────────────────────────────────────
st.write('**Select a Level 3 component to drill into Level 4:**')
depth3_lines = filtered_df[filtered_df['depth']==3]['line'].unique().tolist()
level4 = filtered_df[filtered_df['parent_line'].isin(depth3_lines)]

if not level4.empty:
    parent_opts = level4[['parent_line','parent_name']].drop_duplicates()
    parent_map  = dict(zip(parent_opts['parent_line'].astype(str), parent_opts['parent_name']))
    sel4 = st.selectbox('Select Parent (Level 3)', options=list(parent_map.keys()),
                        format_func=lambda x: parent_map[x], key='sel4')
    level4_chart = level4[level4['parent_line'].astype(str)==sel4][['Date','Name','Values']]
    level4_pivot = level4_chart.pivot_table(index='Date',columns='Name',values='Values')
    show_section(level4_chart, level4_pivot, 'l4')
else:
    st.info('No Level 4 data for this selection.')
