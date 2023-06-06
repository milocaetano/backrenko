import pandas as pd
import backtrader as bt



# Criar um feed de dados usando os dados do Renko
class RenkoData(bt.feeds.PandasData):
    lines = ('uptrend',)
    params = (('uptrend', -1),)


# Adicionar uma estratégia
class RenkoStrategy(bt.Strategy):
    def next(self):
        if not self.position:
            if self.data.uptrend[0] == True:
                self.buy()
        else:
            if self.data.uptrend[0] == False:
                self.sell()
# Carregar os dados do Renko de um arquivo CSV
df = pd.read_csv('renko_data.csv')

# Converter a coluna 'date' para o formato correto
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Criar uma nova instância do Cerebro
cerebro = bt.Cerebro()

# Definir o capital inicial
cerebro.broker.setcash(100000.0)
# Adicionar a estratégia ao Cerebro
cerebro.addstrategy(RenkoStrategy)

# Criar um feed de dados usando os dados do Renko
data = RenkoData(dataname=df)
# Adicionar o feed de dados ao Cerebro
cerebro.adddata(data)

# Imprimir o valor inicial
print('Valor inicial: %.2f' % cerebro.broker.getvalue())

# Rodar o backtest
cerebro.run()

# Imprimir o valor final
print('Valor final: %.2f' % cerebro.broker.getvalue())

# Plotar o resultado
cerebro.plot(style='candlestick')
