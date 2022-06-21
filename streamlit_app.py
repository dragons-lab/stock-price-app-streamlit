# -------------------
# Imports
# -------------------
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

from bs4 import BeautifulSoup
import requests
from datetime import datetime

# today's date
today = datetime.today().strftime('%d %B %Y')
st.set_page_config(layout="wide")


# -------------------
# Web scraping Yahoo Finance
# -------------------
dic = {}
urls = 'https://github.com/dragons-lab/stock-price-app-streamlit/raw/main/stock_info.csv'
#soup = BeautifulSoup(requests.get(url).text)

# read csv from a URL

def space(num_lines=1):
    """Adds empty lines to the Streamlit app."""
    for _ in range(num_lines):
        st.write("")

def num_format(number,format_num=',.2f'):
    """
    Formatting helper - float (1 Item)
    """
    if np.isnan(number):
        return '-'
    return format(number, format_num)


def get_data() -> pd.DataFrame:
    return pd.read_csv(urls)


# Read Data
df = get_data()
# df = pd.read_excel('urls', header=0)

# store values in separate lists and then in a dictionary

symbol_list = list(df['symbol'])
name_list = list(df['name'])
logo_list = list(df['logo'])

#symbol_list = ['AAPL', 'AMZN', 'FB', 'GOOG', 'NFLX']
# name_list = ['Apple', 'Amazon', 'Facebook', 'Alphabet', 'Netflix']


dic['Symbol'] = symbol_list

dic['Name'] = name_list
dic['Logo'] = logo_list


# create a dataframe from dictionary
df_scrape = pd.DataFrame(dic)
df_scrape.Symbol = df_scrape.Symbol
df_scrape.Name = df_scrape.Name
df_scrape.Logo = df_scrape.Logo
dic1 = dict(zip(df_scrape.Symbol, df_scrape.Name))
dic2 = dict(zip(df_scrape.Symbol,  df_scrape.Logo))

# -------------------
# Streamlit Sidebar
# -------------------
#fiat = ['USD', 'EUR', 'GBP']
tokens = df_scrape.Symbol.values

# filters selectbox
st.sidebar.title("Filters")
select_token = st.sidebar.selectbox('Symbol', tokens)
#select_fiat = st.sidebar.selectbox('Fiat', fiat)

# special expander objects
st.sidebar.markdown('***')
with st.sidebar.expander('Help'):
    st.markdown('''
                    - Select symbol  of your choice.
                    - Interactive plots can be zoomed or hovered to retrieve more info.
                    - Plots can be downloaded using Plotly tools.''')

with st.sidebar.expander('Sources'):
    st.markdown('''
    - Python Libraries: yfinance, BeautifulSoup, Plotly, Pandas, Streamlit
    - Prices: https://finance.yahoo.com
    - Logos: https://cryptologos.cc/
    ''')

# Links to socials
st.sidebar.markdown('## Reach Me')
col1, col2, col3, col4 = st.sidebar.columns([2, 2, 2, 3])
with col1:
    link = '[Medium](https://medium.com/@rohithtejam)'
    st.markdown(link, unsafe_allow_html=True)
with col2:
    link = '[LinkedIn](https://www.linkedin.com/in/rohithteja/)'
    st.markdown(link, unsafe_allow_html=True)
with col3:
    link = '[Twitter](https://twitter.com/rohithtejam)'
    st.markdown(link, unsafe_allow_html=True)
with col4:
    link = '[GitHub](https://github.com/rohithteja)'
    st.markdown(link, unsafe_allow_html=True)


# -------------------
# Title Image
# -------------------
col1, col2, col3 = st.columns([1, 5, 3])
with col1:
    st.write("")
with col2:
    #st.image('title.png', width=600)
    st.markdown('# Large-Cap Stocks')
with col3:
     st.write("")
    #st.metric(label="Price", value="70.32", "-8.23%")


# -------------------
# Add crypto logo and name
# -------------------
tickers = yf.Ticker(f'{select_token}')

desc = tickers.info
currentPrice = desc["currentPrice"]
currentOpen = num_format(desc['regularMarketOpen'])
currentLow = num_format(desc['dayLow'])
currentHigh = num_format(desc['regularMarketDayHigh'])
fiftyTwoWeekLow = num_format(desc['fiftyTwoWeekLow'])
fiftyTwoWeekHigh = num_format(desc['fiftyTwoWeekHigh'])
PreviousClose = num_format(desc['regularMarketPreviousClose'])
currentChange = num_format(currentPrice - PreviousClose)
current_PercentChange = num_format((currentChange / PreviousClose) * 100)


col1, col2 , col3, col4 = st.columns([1, 4, 3, 2])
with col1:
    try:
        st.image(f'{dic2[select_token]}', width=70)
    except:
        pass
with col2:
    st.markdown(f'''## {dic1[select_token]}''')
with col3:
    st.write("")
with col4:
    st.metric(label="Price", value = f'{currentPrice}', delta = f'{currentChange} - ({current_PercentChange} %)')


col1, col2 , col3, col4 = st.columns([3, 3, 3, 3])
with col1:
    st.metric(label="Previous Close", value = f'{PreviousClose}' )
with col2:
    st.metric(label="Open", value = f'{currentOpen}')
with col3:
    st.metric(label="Day's Range", value = f'{currentLow} - {currentHigh}')
with col4:
    st.metric(label="52 Week Range", value = f'{fiftyTwoWeekLow} - {fiftyTwoWeekHigh}')



# -------------------
# Candlestick chart with moving averages
# -------------------
st.markdown('''
- The following is an interactive Candlestick chart for the price fluctuations over the past 5 years. 
- Simple moving averages were computed for 20, 50 and 100 day frequencies.
- Aids in trading strategy and to better interpret the price fluctuations.''')

# download 5 year crypto prices from Yahoo Finance
df = yf.download(
    tickers=f'{select_token}', period='5y', interval='1d')

# compute moving averages
df['MA100'] = df.Close.rolling(100).mean()
df['MA50'] = df.Close.rolling(50).mean()
df['MA20'] = df.Close.rolling(20).mean()

# Plotly candlestick chart
fig = go.Figure(data=[go.Candlestick(x=df.index,
                                     open=df.Open,
                                     high=df.High,
                                     low=df.Low,
                                     close=df.Close,
                                     name=f'{select_token}'),
                go.Scatter(x=df.index, y=df.MA20,
                           line=dict(color='yellow', width=1), name='MA20'),
                go.Scatter(x=df.index, y=df.MA50,
                           line=dict(color='green', width=1), name='MA50'),
                go.Scatter(x=df.index, y=df.MA100,
                           line=dict(color='red', width=1), name='MA100')])

fig.update_layout(go.Layout(xaxis={'showgrid': True},
                  yaxis={'showgrid': True}),
                  title=f'{dic1[select_token]} Price Fluctuation with Moving Averages',
                  yaxis_title='Price USD',
                  xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True)

# -------------------
# Line Chart with daily trends
# -------------------
st.markdown('## Yearly Trends')
st.markdown(f'''
- Line graph below shows the price fluctuation of {dic1[select_token]} every day for today's date ({today}).
- The data is automatically updated for the current day.
- The horizontal line shows the current day's start date price.
- Green portion indicates the price greater than start date price and red for lower.
''')

# download daily crypto prices from Yahoo Finance
df = yf.download(
    tickers=f'{select_token}', period='1y', interval='1d')
pio.templates.default = 'plotly_dark'
# Plotly line chart
fig = go.Figure()


fig.add_scattergl(x=df.index, y=df.Close,
                  line={'color': 'green'}, name='Up trend')
fig.add_scattergl(x=df.index, y=df.Close.where(df.Close <= df.Close[0]),
                  line={'color': 'red'}, name='Down trend')
fig.add_hline(y=df.Close[0], line={'color': 'grey'}, name='Trend')
fig.update_layout(go.Layout(xaxis={'showgrid': False},
                  yaxis={'showgrid': False}),
                  title=f'{dic1[select_token]} Daily Trends in Comparison to Open Price',
                  yaxis_title=f'Price USD',
                  xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
