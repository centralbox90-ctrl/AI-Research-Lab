import pandas as pd


def build_features(df):
    """
    Создание признаков для AI модели

    Используем:
    - тренд
    - моментум
    - волатильность
    - силу тренда ADX
    - технические сигналы
    """

    data = df.copy()

    # -------------------------
    # Momentum
    # -------------------------

    data["momentum"] = (
        data["Close"]
        .pct_change(3)
    )


    # -------------------------
    # Trend
    # -------------------------

    data["trend"] = (
        data["Close"]
        .rolling(5)
        .mean()
        -
        data["Close"]
        .rolling(15)
        .mean()
    )


    # -------------------------
    # Volatility
    # -------------------------

    data["volatility"] = (
        data["Close"]
        .rolling(10)
        .std()
    )


    # -------------------------
    # Williams signal
    # -------------------------

    if "Williams_R" in data.columns:

        data["will_signal"] = 0

        data.loc[
            data["Williams_R"] < -80,
            "will_signal"
        ] = 1

        data.loc[
            data["Williams_R"] > -20,
            "will_signal"
        ] = -1


    # -------------------------
    # ADX strength
    # -------------------------

    if "ADX14" in data.columns:

        data["adx_strength"] = data["ADX14"]


    # -------------------------
    # Финальный сигнал
    # -------------------------

    data["market_signal"] = 0


    if "Williams_R" in data.columns:

        data.loc[
            data["Williams_R"] < -80,
            "market_signal"
        ] += 1


        data.loc[
            data["Williams_R"] > -20,
            "market_signal"
        ] -= 1


    if "ADX14" in data.columns:

        data.loc[
            data["ADX14"] > 25,
            "market_signal"
        ] *= 2



    # убираем пустоты после rolling

    data = data.fillna(0)


    return data