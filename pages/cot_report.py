import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from dataloader import cot_report_data

def display_summary_stats(df_diff, key_suffix='1'):
    diff_table = df_diff.copy()
    
    mean = diff_table.mean(numeric_only=True).to_frame("Mean")
    stand_error = diff_table.sem(numeric_only=True).to_frame("Standard Error")
    median = diff_table.median(numeric_only=True).to_frame("Median")
    mode_result = diff_table.mode(numeric_only=True)
    mode = (mode_result.iloc[0] if not mode_result.empty else diff_table.mean(numeric_only=True)).to_frame("Mode")
    std = diff_table.std(numeric_only=True).to_frame("Standard Deviation")
    s_var = diff_table.var(numeric_only=True).to_frame("Sample Variance")
    kurt = diff_table.kurt(numeric_only=True).to_frame("Kurtosis")
    skew = diff_table.skew(numeric_only=True).to_frame("Skew")
    range_stat = diff_table.max(numeric_only=True) - diff_table.min(numeric_only=True)
    range_stat = range_stat.to_frame("Range")
    min_stat = diff_table.min(numeric_only=True).to_frame("Min")
    max_stat = diff_table.max(numeric_only=True).to_frame("Max")
    sum_stat = diff_table.sum(numeric_only=True).to_frame("Sum")
    count = diff_table.count(numeric_only=True).to_frame("Count") 
    
    other_df_stats = pd.concat([mean, stand_error,median,mode, std, s_var, kurt, skew, range_stat, min_stat, max_stat, sum_stat, count], axis=1).round(2)
    other_df_stats = other_df_stats.T.reset_index().rename (columns= {'index': 'Descriptive Statistics'})
    stats_table = other_df_stats
    
    st.dataframe(stats_table, hide_index=True)
    
    st.divider()
    
    std_table = stats_table.copy()
    value_columns = [col for col in std_table.columns if col != 'Descriptive Statistics']
    std_bounce =[{'Standard Deviation Bounds': f'{i} STD {bound}'} for i in [1,2,3] for bound in ['Lower Bound', 'Upper Bound']]
    std_bounce += [{'Standard Deviation Bounds': 'Actual Count'} for _ in range(3)]
    std_bounce += [{'Standard Deviation Bounds': 'Actual % Count'} for _ in range(3)]
    std_bounce += [{'Standard Deviation Bounds': 'Normal % Count'} for _ in range(3)]
    
    posi_prob_adj =[{'Positive Probability Adjusted Return': c} for c in ['Mean Change', 'Count', 'Frequency %', 'Prob Adj Change']]
    nega_prob_adj =[{'Negative Probability Adjusted Return': c} for c in ['Mean Change', 'Count', 'Frequency %', 'Prob Adj Change']]
    zero_prob_adj =[{'Zero Return': c} for c in ['Mean Change', 'Count', 'Frequency %', 'Prob Adj Change']]
    
    percentiles = {'Percentiles' : ['1%', '2%', '3%', '4%', '5%','10%', '25%', '50%', '75%', '90%', '95%', '96%', '97%', '98%', '99%']}
    percentile_values = [1, 2, 3, 4, 5, 10, 25, 50, 75, 90, 95, 96, 97, 98, 99]
    
    for col in value_columns:
        mean_row = std_table.loc[std_table['Descriptive Statistics'] == 'Mean', col].values[0]
        std_row = std_table.loc[std_table['Descriptive Statistics'] == 'Standard Deviation', col].values[0]
        total_count = std_table.loc[std_table['Descriptive Statistics'] == 'Count', col].values[0]
        count_value = diff_table[col].dropna().values
        
        std_bounce[0][col] = round(float(mean_row - (1 * std_row)),2)
        std_bounce[1][col] = round(float(mean_row + (1 * std_row)),2)
        std_bounce[2][col] = round(float(mean_row - (2 * std_row)),2)
        std_bounce[3][col] = round(float(mean_row + (2 * std_row)),2)
        std_bounce[4][col] = round(float(mean_row - (3 * std_row)),2)
        std_bounce[5][col] = round(float(mean_row + (3 * std_row)),2)
        
        std_bounce[6][col] = np.sum((count_value >= std_bounce[0][col]) & (count_value <= std_bounce[1][col]))
        std_bounce[7][col] = np.sum((count_value >= std_bounce[2][col]) & (count_value <= std_bounce[3][col]))
        std_bounce[8][col] = np.sum((count_value >= std_bounce[4][col]) & (count_value <= std_bounce[5][col]))
        
        std_bounce[9][col] = "{:.2%}".format(float(std_bounce[6][col] / total_count)) if total_count else "0%"
        std_bounce[10][col] = "{:.2%}".format(float(std_bounce[7][col] / total_count)) if total_count else "0%"
        std_bounce[11][col] = "{:.2%}".format(float(std_bounce[8][col] / total_count)) if total_count else "0%"
        
        std_bounce[12][col] = "{:.2%}".format(0.6827)
        std_bounce[13][col] = "{:.2%}".format(0.9545)
        std_bounce[14][col] = "{:.2%}".format(0.9973)
        
        posi_mean = np.mean((count_value > 0)) if len(count_value[count_value > 0]) > 0 else 0
        posi_count = np.sum((count_value > 0))
        freq_pct = float(posi_count / total_count) if total_count else 0
        posi_prob_adj[0][col] = round(posi_mean,2)
        posi_prob_adj[1][col] = posi_count
        posi_prob_adj[2][col] = "{:.2%}".format(freq_pct)
        posi_prob_adj[3][col] = round(posi_prob_adj[0][col] * freq_pct,2)
        
        nega_mean = np.mean((count_value < 0)) if len(count_value[count_value < 0]) > 0 else 0
        nega_count = np.sum((count_value < 0))
        freq_pct = float(nega_count / total_count) if total_count else 0
        nega_prob_adj[0][col] = round(nega_mean,2)
        nega_prob_adj[1][col] = nega_count
        nega_prob_adj[2][col] = "{:.2%}".format(freq_pct)
        nega_prob_adj[3][col] = round(nega_prob_adj[0][col] * freq_pct,2)
        
        zero_mean = np.mean((count_value == 0)) if len(count_value[count_value == 0]) > 0 else 0
        zero_count = np.sum((count_value == 0))
        freq_pct = float(zero_count / total_count) if total_count else 0
        zero_prob_adj[0][col] = round(zero_mean,2)
        zero_prob_adj[1][col] = zero_count
        zero_prob_adj[2][col] = "{:.2%}".format(freq_pct)
        zero_prob_adj[3][col] = round(zero_prob_adj[0][col] * freq_pct,2)
        
    std1_bound = pd.DataFrame([std_bounce[0],std_bounce[1],std_bounce[6],std_bounce[9],std_bounce[12]])
    std2_bound = pd.DataFrame([std_bounce[2],std_bounce[3],std_bounce[7],std_bounce[10],std_bounce[13]])
    std3_bound = pd.DataFrame([std_bounce[4],std_bounce[5],std_bounce[8],std_bounce[11],std_bounce[14]])
    positive_adj = pd.DataFrame([posi_prob_adj[0],posi_prob_adj[1],posi_prob_adj[2],posi_prob_adj[3]])
    negative_adj = pd.DataFrame([nega_prob_adj[0],nega_prob_adj[1],nega_prob_adj[2],nega_prob_adj[3]])
    zero_adj = pd.DataFrame([zero_prob_adj[0],zero_prob_adj[1],zero_prob_adj[2],zero_prob_adj[3]])
    
    percentiles_df = pd.DataFrame(percentiles)
    for col in value_columns:
        percentile_values_col = np.nanpercentile(diff_table[col], percentile_values)
        percentiles_df[col] = np.round(percentile_values_col, 2)
        
    st.dataframe(std1_bound, hide_index=True)
    st.dataframe(std2_bound, hide_index=True)
    st.dataframe(std3_bound, hide_index=True)
    st.dataframe(positive_adj, hide_index=True)
    st.dataframe(negative_adj, hide_index=True)
    st.dataframe(zero_adj, hide_index=True)
    st.dataframe(percentiles_df, hide_index=True)
    
    st.divider()
    select_columns = [col for col in diff_table.columns if col != 'Date']
    if select_columns:
        selection = st.radio("Data Type", select_columns, horizontal=True, key=key_suffix)
        if selection:
            distribution = diff_table[selection].dropna().values
            if len(distribution) > 0:
                dis_mean = np.mean(distribution)
                dis_std = np.std(distribution)
                std_interval = [-3,-2.5,-2,-1.75,-1.5,-1.25,-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1,1.25,1.5,1.75,2,2.5,3, np.inf]
                bin_val = [dis_mean + value * dis_std if value is not np.inf else np.inf for value in std_interval]
                bin_label = [round(dis_mean + value * dis_std, 2) if value != np.inf else 'More' for value in std_interval]
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
                
                # Make sure dis_table labels are floats or string 'More' to use :.2% safely
                # Actually, spread values are absolute numbers. Let's just print them directly instead of .2% format.
                # If they are already %, .2% multiplies by 100! But let's follow the standard format used before.
                # Since net_pct_oi is numeric (e.g. 0.05), % is appropriate.
                
                range_label = []
                try:
                    range_label.append(f"Less than {float(dis_table['Bin Label'].iloc[0]):.2%}")
                    for i in range(22):
                        range_label.append(f"{float(dis_table['Bin Label'].iloc[i]):.2%} to {float(dis_table['Bin Label'].iloc[i+1]):.2%}")
                    range_label.append(f"More than {float(dis_table['Bin Label'].iloc[22]):.2%}")
                except Exception:
                    range_label = [str(x) for x in range(24)]
                
                count_prob = dis_table['Count'] / len(distribution)
                cum_prob = count_prob.cumsum()
                
                dis_table['Range'] = range_label
                dis_table['Probability'] = count_prob.apply(lambda x: f"{x*100:.2f}%")
                dis_table['Cum. Probability'] = cum_prob.apply(lambda x: f"{x*100:.2f}%")
                
                chart_table = dis_table.copy()
                chart_table['Probability'] = count_prob * 100
                adjusted_y = [y / 100 for y in chart_table['Probability']]
                
                fig = px.bar(chart_table,x='Range',y=adjusted_y,title=f'{selection} Change Histogram',
                             labels={'y': 'Probability (%)', 'Range': 'Range'},text='Probability')
                fig.update_traces(texttemplate='%{text:.2f}%',textposition='outside')
                fig.update_layout(yaxis=dict(tickformat=".2%"),xaxis=dict(tickangle=-45))
                
                st.dataframe(dis_table,width='stretch', hide_index=True)
                st.plotly_chart(fig)

df = cot_report_data()

st.header("COT Report")

commodities = sorted(df['Commodity'].unique())
selected_commodities = st.multiselect("Select Commodities (Line Charts)", commodities, default=['Gold'])

if selected_commodities:
    for commodity in selected_commodities:
        com_df = df[df['Commodity'] == commodity].copy()
        com_df = com_df.sort_values('Date')

        fig1 = px.line(com_df, x='Date', y='Net % OI', title=f"{commodity} Net % OI")
        fig1.update_layout(xaxis=dict(linecolor='black', linewidth=1, autorange=True, showgrid=True),
                           yaxis=dict(linecolor='black', linewidth=2), autosize=True)
        st.plotly_chart(fig1)
else:
    st.write("Please select at least one commodity.")

st.divider()

single_commodity = st.selectbox("Select Commodity (Detailed Analysis)", commodities, index=commodities.index('Gold'))

single_df = df[df['Commodity'] == single_commodity].copy()
single_df = single_df.sort_values('Date')
single_df['Net % OI Change'] = single_df['Net % OI'].diff()

fig2 = px.bar(single_df, x='Date', y='Net % OI Change', title=f"{single_commodity} Net % OI Change")
fig2.update_layout(xaxis=dict(linecolor='black', linewidth=1, autorange=True, showgrid=True),
                   yaxis=dict(linecolor='black', linewidth=2), autosize=True)

st.plotly_chart(fig2)

st.dataframe(single_df.sort_values('Date', ascending=False).round(2), hide_index=True, width='stretch')

st.divider()

# Compute diff table for all commodities to show summary stats
diff_df = df[['Date', 'Commodity', 'Net % OI']].copy()
diff_df = diff_df.pivot_table(index='Date', columns='Commodity', values='Net % OI').reset_index()
for col in diff_df.columns:
    if col != 'Date':
        diff_df[col] = diff_df[col].diff()

st.subheader("Summary Statistics (Net % OI Change)")
display_summary_stats(diff_df, key_suffix='cot_stats')