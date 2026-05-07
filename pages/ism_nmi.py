import streamlit as st
import pandas as pd
from dataloader import nmi_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


comments,glance_table,index_data,sector_ranking = nmi_data()

st.dataframe(glance_table)
st.dataframe(comments)

st.divider()
#---------------------------------------------------------------------------------------------------------------------------------
index = sector_ranking['Index'].unique()
selection = st.radio('Select Frequency:', index, horizontal=True)
selected_columns = [col for col in sector_ranking.columns if col != 'ID']

sector_ranking_df = sector_ranking[selected_columns]  
sector_ranking_df = sector_ranking_df[sector_ranking_df['Index'] == selection]

index_data_df = index_data[['Date', selection]]
index_data_df['MoM_Diff'] = index_data_df[selection].diff()
index_data_df['YoY_Diff'] = index_data_df[selection].diff(periods=12)

fig1 = px.line(index_data_df, x='Date', y=selection)
fig1.update_layout(xaxis=dict(linecolor='black', linewidth=1,autorange=True,showgrid=True),
                    yaxis=dict(linecolor='black', linewidth=2),autosize=True,
                    #yaxis_range=[(mkt_level_df['Price'].min()) * 0.9, (mkt_level_df['Price'].max()) * 1.2]
                    )
fig1.add_hline(y=50, line_dash="solid", line_color="Black")
fig2 = px.bar(index_data_df, x='Date', y='MoM_Diff')
fig2.update_layout(xaxis=dict(linecolor='black', linewidth=1,autorange=True,showgrid=True),
                    yaxis=dict(linecolor='black', linewidth=2),autosize=True,
                    #yaxis_range=[(mkt_level_df['Price_Pct_Change'].min()) * 1.1, (mkt_level_df['Price_Pct_Change'].max()) * 1.2]
                    )
fig3 = px.bar(index_data_df, x='Date', y='YoY_Diff')
fig3.update_layout(xaxis=dict(linecolor='black', linewidth=1,autorange=True,showgrid=True),
                    yaxis=dict(linecolor='black', linewidth=2),autosize=True,
                    #yaxis_range=[(mkt_level_df['Price_Pct_Change'].min()) * 1.1, (mkt_level_df['Price_Pct_Change'].max()) * 1.2]
                    )

st.plotly_chart(fig1)
st.plotly_chart(fig2)
st.plotly_chart(fig3)
st.dataframe(sector_ranking_df)
st.dataframe(index_data_df)



