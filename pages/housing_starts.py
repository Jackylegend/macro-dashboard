import streamlit as st
import pandas as pd
import numpy as np
from dataloader import housing_starts_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

hs = housing_starts_data()
permit_df = hs[hs['Index Mapping'].str.contains('Permit Authorized', na=False)]
start_df = hs[hs['Index Mapping'].str.contains('Housing Started', na=False)]
comp_df = hs[hs['Index Mapping'].str.contains('Housing Completion', na=False)]
level = ['Permit Authorized in Detail','Housing Started in Detail','Housing Completion in Detail']
index_level = st.radio("Select Index Level", level, horizontal=True, key = 'fig1', )


if index_level == 'Permit Authorized in Detail':
    index_df = permit_df[['Date', 'Name', 'Values']]
    index_df = index_df.pivot_table(index='Date', columns='Name', values='Values').reset_index()
elif index_level == 'Housing Started in Detail':
    index_df = start_df[['Date', 'Name', 'Values']]
    index_df = index_df.pivot_table(index='Date', columns='Name', values='Values').reset_index()
else:
    index_df = comp_df[['Date', 'Name', 'Values']]
    index_df = index_df.pivot_table(index='Date', columns='Name', values='Values').reset_index()

pct_mom = index_df.copy()
pct_yoy = index_df.copy()
for col in pct_mom.columns[1:]:
    pct_mom[col] = pct_mom[col].pct_change() 
for col in pct_yoy.columns[1:]:
    pct_yoy[col] = pct_yoy[col].pct_change(periods=12)

pct_mom = pd.melt(pct_mom,id_vars='Date',var_name='Name',value_name='Values')
pct_yoy = pd.melt(pct_yoy,id_vars='Date',var_name='Name',value_name='Values')

latest_month = pct_mom['Date'].max()
pct_mom = pct_mom[pct_mom['Date'] == latest_month]
pct_yoy = pct_yoy[pct_yoy['Date'] == latest_month]

pct_mom['Values'] = pct_mom['Values'].apply(lambda x: x * 100)
pct_mom = pct_mom.sort_values(by= 'Values', ascending=True)

pct_yoy['Values'] = pct_yoy['Values'].apply(lambda x: x * 100)
pct_yoy = pct_yoy.sort_values(by= 'Values', ascending=True)

fig1 = px.bar(pct_mom, x='Values', y='Name', color='Name')
fig1.update_layout(xaxis=dict(linecolor='black', tickfont=dict(color='black'),title='',linewidth=1,autorange=True,showgrid=True,nticks=10,tickformat=".2f%"),
                    yaxis=dict(linecolor='black', tickfont=dict(color='black'),title='',linewidth=2),autosize=True,height=300)
fig1.update_traces(texttemplate='%{x:.2f}%',textposition='outside',textfont=dict(color='black'))

fig2 = px.bar(pct_yoy, x='Values', y='Name', color='Name')
fig2.update_layout(xaxis=dict(linecolor='black',tickfont=dict(color='black'), title='',linewidth=1,autorange=True,showgrid=True,nticks=10,tickformat=".2f%"),
                    yaxis=dict(linecolor='black',tickfont=dict(color='black'),title='',linewidth=2),autosize=True,height=300)
fig2.update_traces(texttemplate='%{x:.2f}%',textposition='outside',textfont=dict(color='black'))

tab1, tab2 = st.tabs(["YoY", "MoM"])
with tab1:
    st.plotly_chart(fig2,)
with tab2:
    st.plotly_chart(fig1)
    

st.divider()
#-----------------------------------------------------------------------------------------------------------------------------
index_chart = index_df.melt(id_vars="Date",var_name='Name',value_name='Values')
mom = index_df.copy()
for col in mom.columns[1:]:
    mom[col] = mom[col].pct_change()
mom_chart = pd.melt(mom,id_vars='Date',var_name='Name',value_name='Values')
# mom = index_df_level.pct_change().round(4) * 100 
# yoy = index_df.set_index('Date').copy().round(4)
# for col in mom.columns:
#     mom[col] = mom[col].pct_change().round(4) * 100 
# for col in yoy.columns:
#     yoy[col] = yoy[col].pct_change(periods=12).round(4) * 100

tab3, tab4 = st.tabs(["📈 Chart", "🗃 Data"])
with tab3:
    fig3 = px.line(index_chart, x='Date', y='Values', color='Name')
    fig3.add_hline(y=0, line_dash="solid", line_color="black")
    fig3.update_layout(xaxis=dict(linecolor='black', tickfont=dict(color='black'),title='',linewidth=1,autorange=True,showgrid=True,nticks=10),
                            yaxis=dict(tickformat=".2f",linecolor='black', tickfont=dict(color='black'),title='',linewidth=2),autosize=True,height=600)
    fig4 = px.bar(mom_chart, x='Date', y='Values', color='Name')
    fig4.add_hline(y=0, line_dash="solid", line_color="black")
    # y_min, y_max = level1_chart["Values"].min(), level1_chart["Values"].max()
    # tick_interval = (y_max - y_min) / 10  # Adjust 10 ticks for better readability
    # tick_vals = np.arange(y_min, y_max + tick_interval, tick_interval)
    fig4.update_layout(barmode='group',xaxis=dict(linecolor='black', tickfont=dict(color='black'),title='',linewidth=1,autorange=True,showgrid=True,nticks=10),
                            yaxis=dict(tickformat=".2f",linecolor='black', tickfont=dict(color='black'),title='',linewidth=2),autosize=True,height=600)   
    st.plotly_chart(fig3)
    st.plotly_chart(fig4)
with tab4:
    st.dataframe(index_df,width='stretch')
    st.dataframe(mom,width='stretch') 

st.divider()   
#----------------------------------------------------------------------------------------------------------------------
# part3

df_diff = index_df.copy()
freq = st.radio("Select Frequency of Statistics", ['MoM Percentage Change','YoY Percentage Change'], horizontal=True, key = 'stats1')
for col in df_diff.columns[1:]:
    if freq == 'MoM Percentage Change':
        df_diff[col] = df_diff[col].pct_change()
    else:
        df_diff[col] = df_diff[col].pct_change(periods = 12)

mean = df_diff.mean(numeric_only=True).to_frame("Mean")
stand_error = df_diff.sem(numeric_only=True).to_frame("Standard Error")
median = df_diff.median(numeric_only=True).to_frame("Median")
mode_result = df_diff.mode(numeric_only=True)
mode = (mode_result.iloc[0] if not mode_result.empty else df_diff.mean(numeric_only=True)).to_frame("Mode")
std = df_diff.std(numeric_only=True).to_frame("Standard Deviation")
s_var = df_diff.var(numeric_only=True).to_frame("Sample Variance")
kurt = df_diff.kurt(numeric_only=True).to_frame("Kurtosis")
skew = df_diff.skew(numeric_only=True).to_frame("Skew")
range = df_diff.max(numeric_only=True) - df_diff.min(numeric_only=True)
range = range.to_frame("Range")
min = df_diff.min(numeric_only=True).to_frame("Min")
max = df_diff.max(numeric_only=True).to_frame("Max")
sum = df_diff.sum(numeric_only=True).to_frame("Sum")
count = df_diff.count(numeric_only=True).to_frame("Count") 

other_df_stats = pd.concat([mean, stand_error,median,mode, std, s_var, kurt, skew, range, min, max, sum, count], axis=1)
other_df_stats = other_df_stats.T
other_df_stats = other_df_stats.reset_index()
other_df_stats = other_df_stats.rename (columns= {'index': 'Descriptive Statistics'})
stats_table = other_df_stats

st.dataframe(stats_table)

#--------------------------------------------------------------------------------------------------------------
st.divider()

std_table = stats_table.copy()
value_columns = [col for col in std_table.columns if col != 'Descriptive Statistics']
std_bounce =[{'Standard Deviation Bounds': '1 STD Lower Bound'},
            {'Standard Deviation Bounds': '1 STD Upper Bound'},
            {'Standard Deviation Bounds': '2 STD Lower Bound'},
            {'Standard Deviation Bounds': '2 STD Upper Bound'},
            {'Standard Deviation Bounds': '3 STD Lower Bound'},
            {'Standard Deviation Bounds': '3 STD Upper Bound'},
            {'Standard Deviation Bounds': 'Actual Count'},
            {'Standard Deviation Bounds': 'Actual Count'},
            {'Standard Deviation Bounds': 'Actual Count'},
            {'Standard Deviation Bounds': 'Actual % Count'},
            {'Standard Deviation Bounds': 'Actual % Count'},
            {'Standard Deviation Bounds': 'Actual % Count'},
            {'Standard Deviation Bounds': 'Normal % Count'},
            {'Standard Deviation Bounds': 'Normal % Count'},
            {'Standard Deviation Bounds': 'Normal % Count'}]

posi_prob_adj =[{'Positive Probability Adjusted Return': 'Mean Change'},
            {'Positive Probability Adjusted Return': 'Count'},
            {'Positive Probability Adjusted Return': 'Frequency %'},
            {'Positive Probability Adjusted Return': 'Prob Adj Change'}]

nega_prob_adj =[{'Negative Probability Adjusted Return': 'Mean Change'},
            {'Negative Probability Adjusted Return': 'Count'},
            {'Negative Probability Adjusted Return': 'Frequency %'},
            {'Negative Probability Adjusted Return': 'Prob Adj Change'}]

zero_prob_adj =[{'Zero Return': 'Mean Change'},
            {'Zero Return': 'Count'},
            {'Zero Return': 'Frequency %'},
            {'Zero Return': 'Prob Adj Change'}]

percentiles = {'Percentiles' : ['1%', '2%', '3%', '4%', '5%','10%', '25%', '50%', '75%', '90%', '95%', '96%', '97%', '98%', '99%']}
percentile_values = [1, 2, 3, 4, 5, 10, 25, 50, 75, 90, 95, 96, 97, 98, 99]

for col in value_columns:
    mean_row = std_table.loc[std_table['Descriptive Statistics'] == 'Mean', col].values
    std_row = std_table.loc[std_table['Descriptive Statistics'] == 'Standard Deviation', col].values
    total_count = std_table.loc[std_table['Descriptive Statistics'] == 'Count', col].values
    count_value = df_diff[col].values

    std_bounce[0][col] = round(float(mean_row - (1 * std_row)),4)
    std_bounce[1][col] = round(float(mean_row + (1 * std_row)),4)
    std_bounce[2][col] = round(float(mean_row - (2 * std_row)),4)
    std_bounce[3][col] = round(float(mean_row + (2 * std_row)),4)
    std_bounce[4][col] = round(float(mean_row - (3 * std_row)),4)
    std_bounce[5][col] = round(float(mean_row + (3 * std_row)),4)

    std_bounce[6][col] = np.sum((count_value >= std_bounce[0][col]) & (count_value <= std_bounce[1][col]))
    std_bounce[7][col] = np.sum((count_value >= std_bounce[2][col]) & (count_value <= std_bounce[3][col]))
    std_bounce[8][col] = np.sum((count_value >= std_bounce[4][col]) & (count_value <= std_bounce[5][col]))

    std_bounce[9][col] = "{:.2%}".format(float(std_bounce[6][col] / total_count))
    std_bounce[10][col] = "{:.2%}".format(float(std_bounce[7][col] / total_count))
    std_bounce[11][col] = "{:.2%}".format(float(std_bounce[8][col] / total_count))

    std_bounce[12][col] = "{:.2%}".format(0.6827)
    std_bounce[13][col] = "{:.2%}".format(0.9545)
    std_bounce[14][col] = "{:.2%}".format(0.9973)


    std1_bound = pd.DataFrame([std_bounce[0],std_bounce[1],std_bounce[6],std_bounce[9],std_bounce[12]])
    std2_bound = pd.DataFrame([std_bounce[2],std_bounce[3],std_bounce[7],std_bounce[10],std_bounce[13]])
    std3_bound = pd.DataFrame([std_bounce[4],std_bounce[5],std_bounce[8],std_bounce[11],std_bounce[14]])

# Positive prob adjusted return
    posi_mean = np.mean((count_value > 0))
    posi_count = np.sum((count_value > 0))
    freq_pct = float(posi_count / total_count)

    posi_prob_adj[0][col] = round(posi_mean,4)
    posi_prob_adj[1][col] = posi_count
    posi_prob_adj[2][col] = "{:.2%}".format(freq_pct)
    posi_prob_adj[3][col] = round(posi_prob_adj[0][col] * freq_pct,4)

# Negative prob adjusted return
    naga_mean = np.mean((count_value < 0))
    nega_count = np.sum((count_value < 0))
    freq_pct = float(nega_count / total_count)

    nega_prob_adj[0][col] = round(naga_mean,4)
    nega_prob_adj[1][col] = nega_count
    nega_prob_adj[2][col] = "{:.2%}".format(freq_pct)
    nega_prob_adj[3][col] = round(nega_prob_adj[0][col] * freq_pct,4)

# Zero return
    zero_mean = np.mean((count_value == 0))
    zero_count = np.sum((count_value == 0))
    freq_pct = float(zero_count / total_count)

    zero_prob_adj[0][col] = round(zero_mean,4)
    zero_prob_adj[1][col] = zero_count
    zero_prob_adj[2][col] = "{:.2%}".format(freq_pct)
    zero_prob_adj[3][col] = round(zero_prob_adj[0][col] * freq_pct,4)

    positive_adj = pd.DataFrame([posi_prob_adj[0],posi_prob_adj[1],posi_prob_adj[2],posi_prob_adj[3]])
    negative_adj = pd.DataFrame([nega_prob_adj[0],nega_prob_adj[1],nega_prob_adj[2],nega_prob_adj[3]])
    zero_adj = pd.DataFrame([zero_prob_adj[0],zero_prob_adj[1],zero_prob_adj[2],zero_prob_adj[3]])

# Percentiles
percentiles_df = pd.DataFrame(percentiles)
for col in value_columns:
    percentile_values_col = np.nanpercentile(df_diff[col], percentile_values)
    percentiles_df[col] = percentile_values_col

st.dataframe(std1_bound)
st.dataframe(std2_bound)
st.dataframe(std3_bound)
st.dataframe(positive_adj)
st.dataframe(negative_adj)
st.dataframe(zero_adj)
st.dataframe(percentiles_df)

#--------------------------------------------------------------------------------------------------------------------------------------------------------

# Probability Distribution Table
diff_table = df_diff.copy()
select_columns = [col for col in diff_table.columns if col != 'Date']
selection = st.radio("Data Type", select_columns, horizontal=True)
if selection:

    distribution = diff_table[selection].dropna().values
    dis_mean = np.mean(distribution)
    dis_std = np.std(distribution)
    std_interval = [-3,-2.5,-2,-1.75,-1.5,-1.25,-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1,1.25,1.5,1.75,2,2.5,3, np.inf]
    bin_val = [dis_mean + value * dis_std if value is not np.inf else np.inf for value in std_interval]
    bin_label = [round(dis_mean + value * dis_std, 4) if value != np.inf else 'More' for value in std_interval]
    dis_table = pd.DataFrame({'Interval': std_interval,'Bin Value': bin_val,'Bin Label': bin_label})

    try:
        bins = [-np.inf] + dis_table['Bin Value'].tolist()
        cat_result = pd.cut(distribution, bins=bins, labels=False, right=False, include_lowest=True)
        vc = pd.Series(cat_result).value_counts()
        vc.index = vc.index.astype(int)
        value_counts = vc.reindex(np.arange(24), fill_value=0)
    except ValueError:
        value_counts = pd.Series(0, index=np.arange(24))
        value_counts[11] = len(distribution)
    dis_table['Count'] = value_counts

    range_label = [f"Less than {dis_table['Bin Label'][0]:.2%}",f"{dis_table['Bin Label'][0]:.2%} to {dis_table['Bin Label'][1]:.2%}",
                    f"{dis_table['Bin Label'][1]:.2%} to {dis_table['Bin Label'][2]:.2%}",
                    f"{dis_table['Bin Label'][2]:.2%} to {dis_table['Bin Label'][3]:.2%}",
                    f"{dis_table['Bin Label'][3]:.2%} to {dis_table['Bin Label'][4]:.2%}",
                    f"{dis_table['Bin Label'][4]:.2%} to {dis_table['Bin Label'][5]:.2%}",
                    f"{dis_table['Bin Label'][5]:.2%} to {dis_table['Bin Label'][6]:.2%}",
                    f"{dis_table['Bin Label'][6]:.2%} to {dis_table['Bin Label'][7]:.2%}",
                    f"{dis_table['Bin Label'][7]:.2%} to {dis_table['Bin Label'][8]:.2%}",
                    f"{dis_table['Bin Label'][8]:.2%} to {dis_table['Bin Label'][9]:.2%}",
                    f"{dis_table['Bin Label'][9]:.2%} to {dis_table['Bin Label'][10]:.2%}",
                    f"{dis_table['Bin Label'][10]:.2%} to {dis_table['Bin Label'][11]:.2%}",
                    f"{dis_table['Bin Label'][11]:.2%} to {dis_table['Bin Label'][12]:.2%}",
                    f"{dis_table['Bin Label'][12]:.2%} to {dis_table['Bin Label'][13]:.2%}",
                    f"{dis_table['Bin Label'][13]:.2%} to {dis_table['Bin Label'][14]:.2%}",
                    f"{dis_table['Bin Label'][14]:.2%} to {dis_table['Bin Label'][15]:.2%}",
                    f"{dis_table['Bin Label'][15]:.2%} to {dis_table['Bin Label'][16]:.2%}",
                    f"{dis_table['Bin Label'][16]:.2%} to {dis_table['Bin Label'][17]:.2%}",
                    f"{dis_table['Bin Label'][17]:.2%} to {dis_table['Bin Label'][18]:.2%}",
                    f"{dis_table['Bin Label'][18]:.2%} to {dis_table['Bin Label'][19]:.2%}",
                    f"{dis_table['Bin Label'][19]:.2%} to {dis_table['Bin Label'][20]:.2%}",
                    f"{dis_table['Bin Label'][20]:.2%} to {dis_table['Bin Label'][21]:.2%}",
                    f"{dis_table['Bin Label'][21]:.2%} to {dis_table['Bin Label'][22]:.2%}",
                    f"More than {dis_table['Bin Label'][22]:.2%}"]
    count_prob = dis_table['Count'] / pd.Series(distribution).count()
    cum_prob = count_prob.cumsum()

    dis_table['Range'] = range_label
    dis_table['Probability'] = count_prob.apply(lambda x: f"{x*100:.2f}%")
    dis_table['Cum. Probability'] = cum_prob.apply(lambda x: f"{x*100:.2f}%")

    chart_table = dis_table.copy()
    chart_table['Probability'] = count_prob * 100
    adjusted_y = [y / 100 for y in chart_table['Probability']]


    #graph
    tittle_name = f'{selection} Change Histogram'
    fig = px.bar(chart_table,x='Range',y=adjusted_y,title=tittle_name,
                    labels={'y': 'Probability (%)', 'Range': 'Range'},text='Probability')
    fig.update_traces(texttemplate='%{text:.2f}%',textposition='outside')
    fig.update_layout(yaxis=dict(tickformat=".2%"),xaxis=dict(tickangle=-45))

st.dataframe(dis_table,width='stretch')
st.plotly_chart(fig)

#----------------------------------------------------------------------------------------------------------------------------------------------------
st.divider()
