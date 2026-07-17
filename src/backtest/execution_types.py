from enum import Enum


class PositionSide(str, Enum):
    LONG = "BUY"
    SHORT = "SELL"


class DecisionAction(str, Enum):
    OPEN_LONG = "OPEN_LONG"
    OPEN_SHORT = "OPEN_SHORT"
    HOLD = "HOLD"
    CLOSE = "CLOSE"


class ExitReason(str, Enum):
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    MAX_HOLDING = "max_holding"
    DECISION_EXIT = "signal_reverse"
    END_OF_DATA = "final_bar"