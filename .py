from AlgorithmImports import *

class OilTwilightTrader(QCAlgorithm):
    
    def initialize(self):
        self.set_start_date(2024, 1, 31)
        self.set_end_date(2024, 3, 31)  # You can remove or extend this as needed
        self.set_cash(100000)

        # Add WTI and Brent crude oil ETFs
        self.uso = self.add_equity("USO", Resolution.MINUTE).symbol
        self.bno = self.add_equity("BNO", Resolution.MINUTE).symbol

        # Track trade status and what to sell next day
        self.last_trade_date = None
        self.pending_sell_symbols = []

        # Schedule: Buy near market close (1 min before)
        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.before_market_close(self.uso, 1),
            self.buy_oil_positions
        )

        # Schedule: Sell after market open (1 min after)
        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.after_market_open(self.uso, 1),
            self.sell_oil_positions
        )

    def buy_oil_positions(self):
        if self.last_trade_date == self.time.date():
            return  # Already traded today

        self.set_holdings(self.uso, 0.5)
        self.set_holdings(self.bno, 0.5)

        self.pending_sell_symbols = [self.uso, self.bno]
        self.last_trade_date = self.time.date()
        self.debug(f"Bought USO and BNO at market close on {self.time}")

    def sell_oil_positions(self):
        for symbol in self.pending_sell_symbols:
            if self.portfolio[symbol].invested:
                self.liquidate(symbol)
                self.debug(f"Sold {symbol} at market open on {self.time}")
        self.pending_sell_symbols = []
