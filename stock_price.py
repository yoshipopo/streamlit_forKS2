#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:26:25 2022

@author: harukiyoshida
"""
import streamlit as st
import requests
import datetime as dt
#import pandas_datareader.data as web
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import time
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from collections import deque
from pandas_datareader.stooq import StooqDailyReader

st.set_page_config(layout="wide")
def main():
    st.title('モンテカルロシミュレーション')
    path = '/Users/harukiyoshida/Downloads/data_j.xls'
    df_all_company_list = path_to_df_all_company_list(path)
    st.write('全銘柄')
    st.dataframe(df_all_company_list)
    
    selections = st.multiselect('銘柄を複数選択してください',
                                     df_all_company_list['コード&銘柄名'],
                                     ['8306三菱ＵＦＪフィナンシャル・グループ','8591オリックス','9020東日本旅客鉄道','9101日本郵船'],on_change=session_change)
    st.write('選択した銘柄')
    st.dataframe(selections_to_selected_company_list_and_selected_company_list_hyouji(df_all_company_list,selections)[0])
    
    selected_company_list = selections_to_selected_company_list_and_selected_company_list_hyouji(df_all_company_list,selections)[1]
    selected_company_list_hyouji = selections_to_selected_company_list_and_selected_company_list_hyouji(df_all_company_list,selections)[2]
    selected_company_list_hyouji_datenashi = selections
    
    

@st.cache(allow_output_mutation=True)
def button_states():
    return {"pressed": None}

def session_change():
    if "is_pressed" in st.session_state:
        st.session_state["is_pressed"].update({"pressed": None})


@st.cache
def path_to_df_all_company_list(path):
    df_all_company_list = pd.read_excel(path)
    df_all_company_list = df_all_company_list.replace('-', np.nan)
    df_all_company_list['コード&銘柄名'] = df_all_company_list['コード'].astype(str)+df_all_company_list['銘柄名']
    return df_all_company_list


#####銘柄確定させる
#@st.cache(allow_output_mutation=True)
def selections_to_selected_company_list_and_selected_company_list_hyouji(df_all_company_list,selections):
    df_meigarasenntaku_temp = df_all_company_list[df_all_company_list['コード&銘柄名'].isin(selections)]
    selected_company_list = [str(i)+'.JP' for i in df_meigarasenntaku_temp['コード']]
    d = deque(selections)
    d.appendleft('Date')
    selected_company_list_hyouji = list(d)
    return df_meigarasenntaku_temp, selected_company_list, selected_company_list_hyouji

#@st.cache(allow_output_mutation=True)
#@st.cache
def selected_company_list_to_get_df(selected_company_list,selected_company_list_hyouji,duration):
    end = dt.datetime.now()
    start = end-dt.timedelta(days=duration*365)
    for i in range(len(selected_company_list)):
        code = selected_company_list[i]

        stooq = StooqDailyReader(code, start=start, end=end)
        df = stooq.read()  # pandas.core.frame.DataFrame

        df_price = df['Close']
        df_price = df_price.reset_index()

        df_tourakuritu = df['Close']
        df_tourakuritu = df_tourakuritu.pct_change(-1)
        df_tourakuritu = df_tourakuritu.reset_index()
        df_tourakuritu = df_tourakuritu.dropna()
        df_tourakuritu = df_tourakuritu.reset_index(drop=True)

        if i ==0:
          df_price_merged = df_price
          df_tourakuritu_merged = df_tourakuritu
        else:
          df_price_merged=pd.merge(df_price_merged, df_price, on='Date')
          df_tourakuritu_merged=pd.merge(df_tourakuritu_merged, df_tourakuritu, on='Date')
          
    df_price_merged = df_price_merged.set_axis(selected_company_list_hyouji, axis='columns')
    df_tourakuritu_merged = df_tourakuritu_merged.set_axis(selected_company_list_hyouji, axis='columns')
    df_price_merged['Date'] = df_price_merged['Date'].dt.round("D")
    df_tourakuritu_merged['Date'] = df_tourakuritu_merged['Date'].dt.round("D")
    return df_price_merged, df_tourakuritu_merged

if __name__ == "__main__":
    main()