import ccxt
import backtrader as bt
import pandas as pd
from datetime import datetime
from stocktrends import Renko
 
class RenkoStrategy(bt.Strategy):
    params = (('brick_size', 3.0), ('order_pct', 0.95), )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.renko_chart = None
        self.last_brick_direction = None
        self.order = None  # Keep track of an outstanding order

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')  # Change this to `self.log` if you want to use the built-in logging function

    def next(self):
        # Convert the LineBuffer to a DataFrame
        self.log('Next method called')
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
                    # New uptrend: buy if we don't already own the stock
                    if self.order is None and self.broker.getcash() > self.params.order_pct * self.dataclose[0]:
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])
                        self.order = self.buy()
                else:
                    # New downtrend: sell if we own the stock
                    if self.order is None and self.position:
                        self.log('SELL CREATE, %.2f' % self.dataclose[0])
                        self.order = self.sell()
                # Update the last brick direction
                self.last_brick_direction = current_brick_direction

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price,
               order.executed.value,
               order.executed.comm))
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm))
        elif order.status in [order.Canceled, order.Margin]:
            self.log('Order Canceled/Margin')

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
