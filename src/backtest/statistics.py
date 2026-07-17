import pandas as pd


class Statistics:
    """
    Анализ результатов торговли.

    Получает список Trade и рассчитывает
    основные показатели стратегии.
    """

    def __init__(self, trades):
        self.trades = trades

    def calculate(self):
        """
        Возвращает словарь со статистикой.
        """

        if len(self.trades) == 0:
            return {
                "total_trades": 0,
                "buy_trades": 0,
                "sell_trades": 0,
                "win_rate": 0,
                "net_profit": 0,
                "average_profit": 0,
                "best_trade": 0,
                "worst_trade": 0,
                "average_bars": 0,
                "average_drawdown": 0,
                "average_mfe": 0,
            }

        df = pd.DataFrame(
            [trade.as_dict() for trade in self.trades]
        )

        wins = df[df["profit_percent"] > 0]
        losses = df[df["profit_percent"] <= 0]

        stats = {

            "total_trades": len(df),

            "buy_trades":
                (df["side"] == "BUY").sum(),

            "sell_trades":
                (df["side"] == "SELL").sum(),

            "wins":
                len(wins),

            "losses":
                len(losses),

            "win_rate":
                round(
                    len(wins) / len(df) * 100,
                    2
                ),

            "net_profit":
                round(
                    df["profit_percent"].sum(),
                    2
                ),

            "average_profit":
                round(
                    df["profit_percent"].mean(),
                    2
                ),

            "best_trade":
                round(
                    df["profit_percent"].max(),
                    2
                ),

            "worst_trade":
                round(
                    df["profit_percent"].min(),
                    2
                ),

            "average_bars":
                round(
                    df["bars_held"].mean(),
                    2
                ),

            "average_drawdown":
                round(
                    df["max_drawdown_percent"].mean(),
                    2
                ),

            "average_mfe":
                round(
                    df["max_profit_percent"].mean(),
                    2
                ),
        }

        return stats

    def print_report(self):
        """
        Красивый вывод статистики.
        """

        stats = self.calculate()

        print("\n========== BACKTEST REPORT ==========\n")

        print(f"Всего сделок      : {stats['total_trades']}")
        print(f"BUY               : {stats['buy_trades']}")
        print(f"SELL              : {stats['sell_trades']}")

        print()

        print(f"Побед             : {stats['wins']}")
        print(f"Поражений         : {stats['losses']}")
        print(f"Win Rate          : {stats['win_rate']} %")

        print()

        print(f"Общая прибыль     : {stats['net_profit']} %")
        print(f"Средняя сделка    : {stats['average_profit']} %")

        print()

        print(f"Лучшая сделка     : {stats['best_trade']} %")
        print(f"Худшая сделка     : {stats['worst_trade']} %")

        print()

        print(f"Среднее удержание : {stats['average_bars']} баров")
        print(f"Средний MFE       : {stats['average_mfe']} %")
        print(f"Средний MAE       : {stats['average_drawdown']} %")

        print("\n====================================\n")