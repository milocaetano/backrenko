import ccxt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from stocktrends import Renko

# Configurar a conexão com a exchange
exchange = ccxt.binance()

# Obter os dados OHLC para Bitcoin
bars = exchange.fetch_ohlcv('ATOM/USDT', '15m')

# Converter os dados para um DataFrame do pandas
df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'volume'])

# Converter timestamp para datetime
df['date'] = pd.to_datetime(df['date'], unit='ms')
df.to_csv('renko_binance.csv', index=False)
# Renomear as colunas para adequação com a biblioteca stocktrends
df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

# Instanciar um objeto Renko
renko = Renko(df)

# Especificar os parâmetros para o Renko
renko.brick_size = 100

# Gerar o gráfico de Renko
renko_df = renko.get_ohlc_data()

# Salvar o DataFrame em um arquivo CSVimage.png
renko_df.to_csv('renko_data.csv', index=False)
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
