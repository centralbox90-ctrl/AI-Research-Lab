from src.indicators.config import IndicatorConfig



WILLIAMS_CONFIG = IndicatorConfig(

    name="Williams_R",


    parameters={

        "period": 14,

        "overbought": -20,

        "oversold": -80
    },


    optimization_space={

        "period": range(1,51),

        "overbought": [
            -10,
            -20,
            -30
        ],

        "oversold": [
            -70,
            -80,
            -90
        ]
    }
)