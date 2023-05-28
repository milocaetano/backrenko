import ccxt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from stocktrends import Renko

# Configurar a conexão com a exchange
exchange = ccxt.binance()

# Obter os dados OHLC para Bitcoin
bars = exchange.fetch_ohlcv('BTC/USDT', '1d')

# Converter os dados para um DataFrame do pandas
df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

# Converter timestamp para datetime
df['time'] = pd.to_datetime(df['time'], unit='ms')

# Renomear as colunas para adequação com a biblioteca stocktrends
df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

# Instanciar um objeto Renko
renko = Renko(df)

# Especificar os parâmetros para o Renko
renko.brick_size = 100

# Gerar o gráfico de Renko
renko_df = renko.get_ohlc_data()

# Plotar o gráfico de Renko
fig, ax = plt.subplots()

for index, row in renko_df.iterrows():
    if row['uptrend']:
        facecolor = 'green'
    else:
        facecolor = 'red'
    
    # Cria um retângulo representando um "tijolo" no gráfico de Renko
    brick = Rectangle((index, row['low']), 1, row['high'] - row['low'],
                      facecolor=facecolor, edgecolor='black')
    ax.add_patch(brick)

# Ajusta os limites do gráfico e mostra
ax.autoscale_view()
plt.show()
