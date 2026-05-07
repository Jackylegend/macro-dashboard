import streamlit as st
import pandas as pd
import numpy as np
from dataloader import ppi_data, create_bar_chart, create_line_chart
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import math

ppi = ppi_data()
level1 = ppi['Index Level'].unique()
level1 = pd.Series(level1)
level1 = level1[level1.str.match(r'^1(\.\d+)?$')]
l1_df = ppi[(ppi['Index Level'].isin(level1))][['Date', 'Name', 'Values']]
l1_df = l1_df.pivot_table(index='Date', columns='Name', values='Values').reset_index()
pct_mom = l1_df.copy()
pct_yoy = l1_df.copy()


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
                    yaxis=dict(linecolor='black', tickfont=dict(color='black'),title='',linewidth=2),autosize=True,height=800)
fig1.update_traces(texttemplate='%{x:.2f}%',textposition='outside',textfont=dict(color='black'))

fig2 = px.bar(pct_yoy, x='Values', y='Name', color='Name')
fig2.update_layout(xaxis=dict(linecolor='black',tickfont=dict(color='black'), title='',linewidth=1,autorange=True,showgrid=True,nticks=10,tickformat=".2f%"),
                    yaxis=dict(linecolor='black',tickfont=dict(color='black'),title='',linewidth=2),autosize=True,height=800)
fig2.update_traces(texttemplate='%{x:.2f}%',textposition='outside',textfont=dict(color='black'))

tab1, tab2 = st.tabs(["YoY", "MoM"])
with tab1:
    st.plotly_chart(fig2)
with tab2:
    st.plotly_chart(fig1)
    

st.divider()

#---------------------------------------------------------------------------------------------------------------------------------------------    
# Part 2
l1_table = pd.melt(l1_df,id_vars='Date',var_name='Name',value_name='Values')
column_names = l1_table['Name'].unique()
st.write("Select Level 1 Index:")
num_cols = min(5, len(column_names))
cols = st.columns(num_cols)
selected_names = []
for i, name in enumerate(column_names):
    col_index = i % num_cols  # Ensure valid index
    with cols[col_index]:  
        if st.checkbox(name, value=i == 0):  # Default to checked
            selected_names.append(name)
# if selected_names:
level1_chart = l1_table[l1_table['Name'].isin(selected_names)]
l1_df = level1_chart.pivot_table(index='Date', columns='Name', values='Values') # this is the dataframe
pct_mom = l1_df.pct_change().reset_index()
pct_yoy = l1_df.pct_change(periods=12).reset_index()
mom_chart= pd.melt(pct_mom,id_vars='Date',var_name='Name',value_name='Values')
yoy_chart = pd.melt(pct_yoy,id_vars='Date',var_name='Name',value_name='Values')
#------------------------------------------------------------------------------------------------

fig1 = create_line_chart(level1_chart)
fig2 = create_line_chart(mom_chart)
fig3 = create_line_chart(yoy_chart)
tab1, tab2, tab3 = st.tabs(["📈 Line Chart", "🗃 Data Table","🗃 Summary Statistics"])
with tab1:
    st.plotly_chart(fig1,use_container_width=True,key='fig1')
    st.plotly_chart(fig2,use_container_width=True,key='fig2')
    st.plotly_chart(fig3,use_container_width=True,key='fig3')
with tab2:


   st.dataframe(l1_df,width='stretch')
   st.dataframe(pct_mom,width='stretch')
   st.dataframe(pct_yoy,width='stretch')
with tab3:
    df_diff = l1_df.copy()
    #df_diff = df_diff.pivot_table(index='Date', columns='Name', values='Values').reset_index()
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
    selection = st.radio("Select Data Histogram", select_columns, horizontal=True)
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
        st.plotly_chart(fig, key='ppi_dist')

# #--------------------------------------------------------------------------------------------------
parent_index = ppi['Parent Index'].unique()
parent_index = pd.Series(parent_index)
parent_index = parent_index[parent_index.str.match(r'^\d+$')]
level2 = ppi[ppi['Parent Index'].astype(str).isin(parent_index)]

parent_map = dict(zip(level2['Parent Index'].astype(str), level2['Parent Name']))
selected_parent_index = st.selectbox("Select Parent Category", options=list(parent_map.keys()), format_func=lambda x: parent_map[x], key='ppi_l2_select')
level2_chart = level2[level2['Parent Index'].astype(str) == selected_parent_index][['Date', 'Name', 'Values']]
level2_df = level2_chart.pivot_table(index='Date', columns='Name', values='Values')
l2_mom = level2_df.pct_change().reset_index()
l2_yoy = level2_df.pct_change(periods=12).reset_index()
l2_mom_chart= pd.melt(l2_mom,id_vars='Date',var_name='Name',value_name='Values')
l2_yoy_chart = pd.melt(l2_yoy,id_vars='Date',var_name='Name',value_name='Values')

fig1 = create_line_chart(level2_chart)
fig2 = create_line_chart(l2_mom_chart)
fig3 = create_line_chart(l2_yoy_chart)

tab3, tab4 = st.tabs(["📈 Chart", "🗃 Data"])
with tab3:
    st.plotly_chart(fig1,use_container_width=True,key='fig4')
    st.plotly_chart(fig2,use_container_width=True,key='fig5')
    st.plotly_chart(fig3,use_container_width=True,key='fig6')
with tab4:

    st.dataframe(level2_df,width='stretch' )
    st.dataframe(l2_mom,width='stretch')
    st.dataframe(l2_yoy,width='stretch') 

st.divider()   
# #----------------------------------------------------------------------------------------------------------------------
st.write('Please select parent level 3 index of sub-components')
# Filter for '1.xx' format parent indices (e.g. 1.01, 1.02)
level3 = ppi[ppi['Parent Index'].notna() & ppi['Parent Index'].str.match(r'^\d+\.\d+$')]
# Extract unique Parent Index values
l3_index = level3['Parent Index'].unique()
parent_map = dict(zip(level3['Parent Index'].astype(str), level3['Parent Name']))

level3 = level3[level3['Parent Index'].astype(str).isin(l3_index)]
if not parent_map:
    st.info("No sub-components available at this level.")
    st.stop()
selected_parent_index = st.selectbox("Select Parent Category", options=list(parent_map.keys()), format_func=lambda x: parent_map[x], key='ppi_l3_select')
level3_chart = ppi[ppi['Parent Index'].astype(str) == selected_parent_index][['Date', 'Name', 'Values']]
level3_df = level3_chart.pivot_table(index='Date', columns='Name', values='Values')


l3_mom = level3_df.pct_change().reset_index()
l3_yoy = level3_df.pct_change(periods=12).reset_index()
l3_mom_chart= pd.melt(l3_mom,id_vars='Date',var_name='Name',value_name='Values')
l3_yoy_chart = pd.melt(l3_yoy,id_vars='Date',var_name='Name',value_name='Values')

fig1 = create_line_chart(level3_chart)
fig2 = create_line_chart(l3_mom_chart)
fig3 = create_line_chart(l3_yoy_chart)


tab3, tab4 = st.tabs(["📈 Chart", "🗃 Data"])
with tab3:
    st.plotly_chart(fig1,key='fig7')
    st.plotly_chart(fig2,key='fig8')
    st.plotly_chart(fig3,key='fig9')
with tab4:

    st.dataframe(level3_df,width='stretch' )
    st.dataframe(l3_mom,width='stretch')
    st.dataframe(l3_yoy,width='stretch') 

st.divider()   
# #----------------------------------------------------------------------------------------------------------------------
st.write('Please select parent level 4 index of sub-components')
# Filter for '1.xx.xx' format parent indices (deeper sub-components)
level4 = ppi[ppi['Parent Index'].notna() & ppi['Parent Index'].str.match(r'^\d+\.\d+\.\d+$')]
# Extract unique Parent Index values
l4_index = level4['Parent Index'].unique()

parent_map = dict(zip(level4['Parent Index'].astype(str), level4['Parent Name']))
level4 = level4[level4['Parent Index'].astype(str).isin(l4_index)]
if not parent_map:
    st.info("No sub-components available at this level.")
    st.stop()
selected_parent_index = st.selectbox("Select Parent Category", options=list(parent_map.keys()), format_func=lambda x: parent_map[x], key='ppi_l4_select')
level4_chart = ppi[ppi['Parent Index'].astype(str) == selected_parent_index][['Date', 'Name', 'Values']]

level4_df = level4_chart.pivot_table(index='Date', columns='Name', values='Values')

l4_mom = level4_df.pct_change().reset_index()
l4_yoy = level4_df.pct_change(periods=12).reset_index()
l4_mom_chart= pd.melt(l4_mom,id_vars='Date',var_name='Name',value_name='Values')
l4_yoy_chart = pd.melt(l4_yoy,id_vars='Date',var_name='Name',value_name='Values')

fig1 = create_line_chart(level4_chart)
fig2 = create_line_chart(l4_mom_chart)
fig3 = create_line_chart(l4_yoy_chart)

tab3, tab4 = st.tabs(["📈 Chart", "🗃 Data"])
with tab3:
    st.plotly_chart(fig1,key='fig10')
    st.plotly_chart(fig2,key='fig11')
    st.plotly_chart(fig3,key='fig12')

with tab4:
    st.dataframe(level4_df,width='stretch' )
    st.dataframe(l4_mom,width='stretch')
    st.dataframe(l4_yoy,width='stretch')

#--------------------------------------------------------------------------------------------------------------
#part3
#index_level_1 = st.radio("Select Index Level", level1, horizontal=True, key = 'stats_table')

# df_diff= l1_df
# #df_diff = df_diff.pivot_table(index='Date', columns='Name', values='Values').reset_index()
# freq = st.radio("Select Frequency of Statistics", ['MoM Percentage Change','YoY Percentage Change'], horizontal=True, key = 'stats2')
# for col in df_diff.columns[1:]:

#     if freq == 'MoM Percentage Change':
#         df_diff[col] = df_diff[col].pct_change()
#     else:
#         df_diff[col] = df_diff[col].pct_change(periods = 12)

# mean = df_diff.mean(numeric_only=True).to_frame("Mean")
# stand_error = df_diff.sem(numeric_only=True).to_frame("Standard Error")
# median = df_diff.median(numeric_only=True).to_frame("Median")
# mode = df_diff.mode(numeric_only=True).iloc[0].to_frame("Mode")
# std = df_diff.std(numeric_only=True).to_frame("Standard Deviation")
# s_var = df_diff.var(numeric_only=True).to_frame("Sample Variance")
# kurt = df_diff.kurt(numeric_only=True).to_frame("Kurtosis")
# skew = df_diff.skew(numeric_only=True).to_frame("Skew")
# range = df_diff.max(numeric_only=True) - df_diff.min(numeric_only=True)
# range = range.to_frame("Range")
# min = df_diff.min(numeric_only=True).to_frame("Min")
# max = df_diff.max(numeric_only=True).to_frame("Max")
# sum = df_diff.sum(numeric_only=True).to_frame("Sum")
# count = df_diff.count(numeric_only=True).to_frame("Count") 

# other_df_stats = pd.concat([mean, stand_error,median,mode, std, s_var, kurt, skew, range, min, max, sum, count], axis=1)
# other_df_stats = other_df_stats.T
# other_df_stats = other_df_stats.reset_index()
# other_df_stats = other_df_stats.rename (columns= {'index': 'Descriptive Statistics'})
# stats_table = other_df_stats

# st.dataframe(stats_table)

# #--------------------------------------------------------------------------------------------------------------
# st.divider()

# std_table = stats_table.copy()
# value_columns = [col for col in std_table.columns if col != 'Descriptive Statistics']
# std_bounce =[{'Standard Deviation Bounds': '1 STD Lower Bound'},
#             {'Standard Deviation Bounds': '1 STD Upper Bound'},
#             {'Standard Deviation Bounds': '2 STD Lower Bound'},
#             {'Standard Deviation Bounds': '2 STD Upper Bound'},
#             {'Standard Deviation Bounds': '3 STD Lower Bound'},
#             {'Standard Deviation Bounds': '3 STD Upper Bound'},
#             {'Standard Deviation Bounds': 'Actual Count'},
#             {'Standard Deviation Bounds': 'Actual Count'},
#             {'Standard Deviation Bounds': 'Actual Count'},
#             {'Standard Deviation Bounds': 'Actual % Count'},
#             {'Standard Deviation Bounds': 'Actual % Count'},
#             {'Standard Deviation Bounds': 'Actual % Count'},
#             {'Standard Deviation Bounds': 'Normal % Count'},
#             {'Standard Deviation Bounds': 'Normal % Count'},
#             {'Standard Deviation Bounds': 'Normal % Count'}]

# posi_prob_adj =[{'Positive Probability Adjusted Return': 'Mean Change'},
#             {'Positive Probability Adjusted Return': 'Count'},
#             {'Positive Probability Adjusted Return': 'Frequency %'},
#             {'Positive Probability Adjusted Return': 'Prob Adj Change'}]

# nega_prob_adj =[{'Negative Probability Adjusted Return': 'Mean Change'},
#             {'Negative Probability Adjusted Return': 'Count'},
#             {'Negative Probability Adjusted Return': 'Frequency %'},
#             {'Negative Probability Adjusted Return': 'Prob Adj Change'}]

# zero_prob_adj =[{'Zero Return': 'Mean Change'},
#             {'Zero Return': 'Count'},
#             {'Zero Return': 'Frequency %'},
#             {'Zero Return': 'Prob Adj Change'}]

# percentiles = {'Percentiles' : ['1%', '2%', '3%', '4%', '5%','10%', '25%', '50%', '75%', '90%', '95%', '96%', '97%', '98%', '99%']}
# percentile_values = [1, 2, 3, 4, 5, 10, 25, 50, 75, 90, 95, 96, 97, 98, 99]

# for col in value_columns:
#     mean_row = std_table.loc[std_table['Descriptive Statistics'] == 'Mean', col].values
#     std_row = std_table.loc[std_table['Descriptive Statistics'] == 'Standard Deviation', col].values
#     total_count = std_table.loc[std_table['Descriptive Statistics'] == 'Count', col].values
#     count_value = df_diff[col].values

#     std_bounce[0][col] = round(float(mean_row - (1 * std_row)),4)
#     std_bounce[1][col] = round(float(mean_row + (1 * std_row)),4)
#     std_bounce[2][col] = round(float(mean_row - (2 * std_row)),4)
#     std_bounce[3][col] = round(float(mean_row + (2 * std_row)),4)
#     std_bounce[4][col] = round(float(mean_row - (3 * std_row)),4)
#     std_bounce[5][col] = round(float(mean_row + (3 * std_row)),4)

#     std_bounce[6][col] = np.sum((count_value >= std_bounce[0][col]) & (count_value <= std_bounce[1][col]))
#     std_bounce[7][col] = np.sum((count_value >= std_bounce[2][col]) & (count_value <= std_bounce[3][col]))
#     std_bounce[8][col] = np.sum((count_value >= std_bounce[4][col]) & (count_value <= std_bounce[5][col]))

#     std_bounce[9][col] = "{:.2%}".format(float(std_bounce[6][col] / total_count))
#     std_bounce[10][col] = "{:.2%}".format(float(std_bounce[7][col] / total_count))
#     std_bounce[11][col] = "{:.2%}".format(float(std_bounce[8][col] / total_count))

#     std_bounce[12][col] = "{:.2%}".format(0.6827)
#     std_bounce[13][col] = "{:.2%}".format(0.9545)
#     std_bounce[14][col] = "{:.2%}".format(0.9973)


#     std1_bound = pd.DataFrame([std_bounce[0],std_bounce[1],std_bounce[6],std_bounce[9],std_bounce[12]])
#     std2_bound = pd.DataFrame([std_bounce[2],std_bounce[3],std_bounce[7],std_bounce[10],std_bounce[13]])
#     std3_bound = pd.DataFrame([std_bounce[4],std_bounce[5],std_bounce[8],std_bounce[11],std_bounce[14]])

# # Positive prob adjusted return
#     posi_mean = np.mean((count_value > 0))
#     posi_count = np.sum((count_value > 0))
#     freq_pct = float(posi_count / total_count)

#     posi_prob_adj[0][col] = round(posi_mean,4)
#     posi_prob_adj[1][col] = posi_count
#     posi_prob_adj[2][col] = "{:.2%}".format(freq_pct)
#     posi_prob_adj[3][col] = round(posi_prob_adj[0][col] * freq_pct,4)

# # Negative prob adjusted return
#     naga_mean = np.mean((count_value < 0))
#     nega_count = np.sum((count_value < 0))
#     freq_pct = float(nega_count / total_count)

#     nega_prob_adj[0][col] = round(naga_mean,4)
#     nega_prob_adj[1][col] = nega_count
#     nega_prob_adj[2][col] = "{:.2%}".format(freq_pct)
#     nega_prob_adj[3][col] = round(nega_prob_adj[0][col] * freq_pct,4)

# # Zero return
#     zero_mean = np.mean((count_value == 0))
#     zero_count = np.sum((count_value == 0))
#     freq_pct = float(zero_count / total_count)

#     zero_prob_adj[0][col] = round(zero_mean,4)
#     zero_prob_adj[1][col] = zero_count
#     zero_prob_adj[2][col] = "{:.2%}".format(freq_pct)
#     zero_prob_adj[3][col] = round(zero_prob_adj[0][col] * freq_pct,4)

#     positive_adj = pd.DataFrame([posi_prob_adj[0],posi_prob_adj[1],posi_prob_adj[2],posi_prob_adj[3]])
#     negative_adj = pd.DataFrame([nega_prob_adj[0],nega_prob_adj[1],nega_prob_adj[2],nega_prob_adj[3]])
#     zero_adj = pd.DataFrame([zero_prob_adj[0],zero_prob_adj[1],zero_prob_adj[2],zero_prob_adj[3]])

# # Percentiles
# percentiles_df = pd.DataFrame(percentiles)
# for col in value_columns:
#     percentile_values_col = np.nanpercentile(df_diff[col], percentile_values)
#     percentiles_df[col] = percentile_values_col

# st.dataframe(std1_bound)
# st.dataframe(std2_bound)
# st.dataframe(std3_bound)
# st.dataframe(positive_adj)
# st.dataframe(negative_adj)
# st.dataframe(zero_adj)
# st.dataframe(percentiles_df)

# #--------------------------------------------------------------------------------------------------------------------------------------------------------

# # Probability Distribution Table
# diff_table = df_diff.copy()
# select_columns = [col for col in diff_table.columns if col != 'Date']
# selection = st.radio("Data Type", select_columns, horizontal=True)
# if selection:

#     distribution = diff_table[selection].dropna().values
#     dis_mean = np.mean(distribution)
#     dis_std = np.std(distribution)
#     std_interval = [-3,-2.5,-2,-1.75,-1.5,-1.25,-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1,1.25,1.5,1.75,2,2.5,3, np.inf]
#     bin_val = [dis_mean + value * dis_std if value is not np.inf else np.inf for value in std_interval]
#     bin_label = [round(dis_mean + value * dis_std, 4) if value != np.inf else 'More' for value in std_interval]
#     dis_table = pd.DataFrame({'Interval': std_interval,'Bin Value': bin_val,'Bin Label': bin_label})

#     bins = [-np.inf] + dis_table['Bin Value'].tolist()
#     categories = pd.cut(distribution, bins=bins, labels=False, right=False,include_lowest=True)
#     value_counts = pd.Series(categories).value_counts().sort_index()
#     dis_table['Count'] = value_counts

#     range_label = [f"Less than {dis_table['Bin Label'][0]:.2%}",f"{dis_table['Bin Label'][0]:.2%} to {dis_table['Bin Label'][1]:.2%}",
#                     f"{dis_table['Bin Label'][1]:.2%} to {dis_table['Bin Label'][2]:.2%}",
#                     f"{dis_table['Bin Label'][2]:.2%} to {dis_table['Bin Label'][3]:.2%}",
#                     f"{dis_table['Bin Label'][3]:.2%} to {dis_table['Bin Label'][4]:.2%}",
#                     f"{dis_table['Bin Label'][4]:.2%} to {dis_table['Bin Label'][5]:.2%}",
#                     f"{dis_table['Bin Label'][5]:.2%} to {dis_table['Bin Label'][6]:.2%}",
#                     f"{dis_table['Bin Label'][6]:.2%} to {dis_table['Bin Label'][7]:.2%}",
#                     f"{dis_table['Bin Label'][7]:.2%} to {dis_table['Bin Label'][8]:.2%}",
#                     f"{dis_table['Bin Label'][8]:.2%} to {dis_table['Bin Label'][9]:.2%}",
#                     f"{dis_table['Bin Label'][9]:.2%} to {dis_table['Bin Label'][10]:.2%}",
#                     f"{dis_table['Bin Label'][10]:.2%} to {dis_table['Bin Label'][11]:.2%}",
#                     f"{dis_table['Bin Label'][11]:.2%} to {dis_table['Bin Label'][12]:.2%}",
#                     f"{dis_table['Bin Label'][12]:.2%} to {dis_table['Bin Label'][13]:.2%}",
#                     f"{dis_table['Bin Label'][13]:.2%} to {dis_table['Bin Label'][14]:.2%}",
#                     f"{dis_table['Bin Label'][14]:.2%} to {dis_table['Bin Label'][15]:.2%}",
#                     f"{dis_table['Bin Label'][15]:.2%} to {dis_table['Bin Label'][16]:.2%}",
#                     f"{dis_table['Bin Label'][16]:.2%} to {dis_table['Bin Label'][17]:.2%}",
#                     f"{dis_table['Bin Label'][17]:.2%} to {dis_table['Bin Label'][18]:.2%}",
#                     f"{dis_table['Bin Label'][18]:.2%} to {dis_table['Bin Label'][19]:.2%}",
#                     f"{dis_table['Bin Label'][19]:.2%} to {dis_table['Bin Label'][20]:.2%}",
#                     f"{dis_table['Bin Label'][20]:.2%} to {dis_table['Bin Label'][21]:.2%}",
#                     f"{dis_table['Bin Label'][21]:.2%} to {dis_table['Bin Label'][22]:.2%}",
#                     f"More than {dis_table['Bin Label'][22]:.2%}"]
#     count_prob = dis_table['Count'] / pd.Series(distribution).count()
#     cum_prob = count_prob.cumsum()

#     dis_table['Range'] = range_label
#     dis_table['Probability'] = count_prob.apply(lambda x: f"{x*100:.2f}%")
#     dis_table['Cum. Probability'] = cum_prob.apply(lambda x: f"{x*100:.2f}%")

#     chart_table = dis_table.copy()
#     chart_table['Probability'] = count_prob * 100
#     adjusted_y = [y / 100 for y in chart_table['Probability']]


#     #graph
#     tittle_name = f'{selection} Change Histogram'
#     fig = px.bar(chart_table,x='Range',y=adjusted_y,title=tittle_name,
#                     labels={'y': 'Probability (%)', 'Range': 'Range'},text='Probability')
#     fig.update_traces(texttemplate='%{text:.2f}%',textposition='outside')
#     fig.update_layout(yaxis=dict(tickformat=".2%"),xaxis=dict(tickangle=-45))

# st.dataframe(dis_table,width='stretch')
# st.plotly_chart(fig,key='fig13')

# #----------------------------------------------------------------------------------------------------------------------------------------------------
# st.divider()



# index_mapping = cpi['Index Mapping'].unique()
# mapping = st.radio("Select Index Level", mapping, horizontal=True)
# index_mapping = cpi[(cpi['Index Level'] == level)]

# st.dataframe(index_level_df)
# st.dataframe(index_mapping_df)


#----------------------------------------------------------------------------------------------------------------------------------------------------