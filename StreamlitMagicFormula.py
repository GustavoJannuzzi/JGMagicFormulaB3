import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import streamlit as st

##################
# MAGIC FORMULA
##################

# função para converter valores percentuais para valores decimais
def convert_perc(value):
    return pd.to_numeric(value.replace('%','').replace('.', '').replace(',', '.'))

# mapeando colunas que possuem valores percentuais
convs = {5: convert_perc, 12: convert_perc, 13: convert_perc, 15: convert_perc, 16: convert_perc, 20: convert_perc}

url = 'http://fundamentus.com.br/resultado.php'
agent = {"User-Agent":"Mozzila/5.0"}
resposta = requests.get(url, headers = agent)
soup = BeautifulSoup(resposta.text, 'lxml')
tabela = soup.find_all('table')[0]
df = pd.read_html(str(tabela), decimal = ',', thousands='.', converters=convs)[0]
#df = pd.read_html(str(tabela), decimal = ',', thousands='.',index_col='Papel', converters=convs)[0]

fundamentus = df

# empresas que possuem alguma liquidez
fundamentus = fundamentus[fundamentus['Liq.2meses'] > 1000000]

# com retornos positivos
fundamentus = fundamentus[fundamentus['ROIC'] > 0]
fundamentus = fundamentus[fundamentus['EV/EBIT'] > 0]

#Maiorliquidez
fundamentus = fundamentus[fundamentus['Patrim. Líq'] > 0]

fundamentusNovo = fundamentus[['Papel', 'ROIC','EV/EBIT','P/L']]

EvOrdenado = fundamentusNovo.sort_values(by = 'EV/EBIT')
EvOrdenado = EvOrdenado.reset_index(drop = True)
EvOrdenado['EvOrdenado'] = EvOrdenado.index

roicOrdenado = EvOrdenado.sort_values(by = 'ROIC', ascending = False)
roicOrdenado = roicOrdenado.reset_index(drop = True)
roicOrdenado['ROICOrdenado'] = roicOrdenado.index
dados = roicOrdenado

dados['score'] = dados['EvOrdenado'] + dados['ROICOrdenado']
dados.sort_values(by = 'score')

dados['Papel'] = dados['Papel'] +'.SA'

stockSectorDF = 'https://raw.githubusercontent.com/GustavoJannuzzi/JGMagicFormulaB3/main/StockSector.csv'
stockSectorDF = pd.read_csv(stockSectorDF)
del stockSectorDF['Unnamed: 0']

dadosNovos = pd.merge(dados, stockSectorDF, on ='Papel', how='inner')

#Excluir setores 
filtroSetores = dadosNovos[dadosNovos['sector'] != 'Financial Services']
filtroSetores = filtroSetores[filtroSetores['sector'] != 'Energy']
filtroSetores = filtroSetores[filtroSetores['sector'] != 'Utilities']
filtroSetores = filtroSetores[filtroSetores['sector'] != 'NA']

# Ranking da Magic Formula
# MagicWallet = filtroSetores.sort_values(by = 'score').head(QtdStocks)


################
#  STREAMLIT
################


st.title("Magic Formula - B3")

QtdStocks = st.slider('How many stocks?',10,50,20,10)
# Ranking da Magic Formula
MagicWallet = filtroSetores.sort_values(by = 'score').head(QtdStocks)

Clickerd = st.button("RUN THE MAGIC")
if Clickerd:
    st.dataframe(MagicWallet)
