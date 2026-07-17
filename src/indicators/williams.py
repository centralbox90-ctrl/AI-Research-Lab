class WilliamsIndicator:
    """
    Williams %R индикатор.

    Работает через IndicatorConfig.
    """


    def __init__(self, config):

        self.config = config

        self.period = config.get(
            "period",
            14
        )


        self.name = config.name



    def calculate(self, history):

        if len(history) < self.period:
            return None


        highs = [
            x.high
            for x in history[-self.period:]
        ]

        lows = [
            x.low
            for x in history[-self.period:]
        ]


        close = history[-1].close


        highest_high = max(highs)

        lowest_low = min(lows)


        if highest_high == lowest_low:
            return 0


        value = (

            (
                highest_high - close
            )
            /
            (
                highest_high - lowest_low
            )

        ) * -100


        return value