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

### Test 2 ###
from AlgorithmImports import *

class OilTwilightTrader(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 30)
        self.set_end_date(2024, 6, 30)
        self.set_cash(100000)

        # Add WTI and Brent crude oil ETFs
        self.uso = self.add_equity("USO").symbol
        self.bno = self.add_equity("BNO").symbol

        self.last_trade_date = None
        self.pending_sell_symbols = []

        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.before_market_close(self.uso, 1),
            self.buy_oil_positions
        )

        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.after_market_open(self.uso, 1),
            self.sell_oil_positions
        )

    def compute_trend_heat(self, symbol):
        history = self.history(symbol, 200, Resolution.DAILY)
        if history.empty or "close" not in history.columns:
            return 0.0

        closes = history["close"]
        if len(closes) < 200:
            return 0.0

        short_ma = closes[-10:].mean()
        medium_ma = closes[-50:].mean()
        long_ma = closes.mean()

        heat_score = 0.0

        if short_ma > medium_ma:
            heat_score += 0.3
        elif short_ma < medium_ma:
            heat_score -= 0.3

        if medium_ma > long_ma:
            heat_score += 0.3
        elif medium_ma < long_ma:
            heat_score -= 0.3

        if short_ma > long_ma:
            heat_score += 0.4
        elif short_ma < long_ma:
            heat_score -= 0.4

        self.plot(f"{symbol} TrendHeat", "Score", heat_score)
        return heat_score

    def buy_oil_positions(self):
        if self.last_trade_date == self.time.date():
            return

        uso_score = self.compute_trend_heat(self.uso)
        bno_score = self.compute_trend_heat(self.bno)

        if uso_score < -0.6 or bno_score < -0.6:
            self.debug(f"Skipping buy due to weak trend | USO:{uso_score:.2f}, BNO:{bno_score:.2f}")
            return

        uso_weight = 0.5 + 0.5 * uso_score
        bno_weight = 0.5 + 0.5 * bno_score

        total_weight = uso_weight + bno_weight
        if total_weight > 1.0:
            scale = 1.0 / total_weight
            uso_weight *= scale
            bno_weight *= scale

        self.set_holdings(self.uso, uso_weight)
        self.set_holdings(self.bno, bno_weight)

        self.pending_sell_symbols = [self.uso, self.bno]
        self.last_trade_date = self.time.date()
        self.debug(f"Bought USO({uso_weight:.2f}) and BNO({bno_weight:.2f}) based on trend heat")

    def sell_oil_positions(self):
        for symbol in self.pending_sell_symbols:
            if self.portfolio[symbol].invested:
                self.liquidate(symbol)
                self.debug(f"Sold {symbol} at market open on {self.time}")
        self.pending_sell_symbols = []

