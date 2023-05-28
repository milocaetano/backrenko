import ccxt
import backtrader as bt
import pandas as pd
from datetime import datetime
from stocktrends import Renko

class RenkoStrategy(bt.Strategy):
    params = (('brick_size', 3.0), )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.renko_chart = None
        self.last_brick_direction = None  # Add this line

    def next(self):
        # Convert the LineBuffer to a DataFrame
        df = pd.DataFrame({
            'date': [bt.num2date(x) for x in list(self.datas[0].datetime)],
            'close': list(self.dataclose),
            'open': list(self.datas[0].open),
            'high': list(self.datas[0].high),
            'low': list(self.datas[0].low),
            'volume': list(self.datas[0].volume),
        })

        # Initialize the Renko chart once we have enough data
        if self.renko_chart is None and len(df) >= self.params.brick_size:
            renko_obj = Renko(df)
            renko_obj.brick_size = self.params.brick_size
            self.renko_chart = renko_obj.get_ohlc_data()  # Get the OHLC representation
            # Set the last brick direction
            self.last_brick_direction = self.renko_chart['uptrend'].iloc[-1]
        elif self.renko_chart is not None:
            # Update the Renko chart with the new data
            renko_obj = Renko(df)
            renko_obj.brick_size = self.params.brick_size
            self.renko_chart = renko_obj.get_ohlc_data()  # Get the OHLC representation
            # Check if the brick direction has changed
            current_brick_direction = self.renko_chart['uptrend'].iloc[-1]
            if current_brick_direction != self.last_brick_direction:
                # The brick direction has changed
                if current_brick_direction:
                    # New uptrend: buy
                    self.buy()
                else:
                    # New downtrend: sell
                    self.sell()
                # Update the last brick direction
                self.last_brick_direction = current_brick_direction

# Configurando o Cerebro
cerebro = bt.Cerebro()
cerebro.addstrategy(RenkoStrategy)

# Use ccxt para baixar dados de BTC/USD
exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h')
df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

# Adicione seus dados ao Cerebro e defina o dinheiro inicial
data = bt.feeds.PandasData(dataname=df, datetime=-1)
cerebro.adddata(data)
cerebro.broker.setcash(10000.0)

# Execute o backtest
cerebro.run()

# Traçar o gráfico
cerebro.plot()
