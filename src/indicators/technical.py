import pandas as pd


def williams_r(df, period=14):

    high = df["High"].rolling(period).max()
    low = df["Low"].rolling(period).min()

    return -100 * ((high - df["Close"]) / (high - low))


def sma(df, period=14):

    return df["Close"].rolling(period).mean()



def ema(df, period=14):

    return df["Close"].ewm(
        span=period,
        adjust=False
    ).mean()



def rsi(df, period=14):

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)


    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()


    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))



def macd(df):

    ema12 = df["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = df["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    return ema12 - ema26



def adx(df, period=14):

    high = df["High"]
    low = df["Low"]
    close = df["Close"]


    plus_dm = high.diff()
    minus_dm = -low.diff()


    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0


    tr1 = high - low

    tr2 = abs(
        high - close.shift()
    )

    tr3 = abs(
        low - close.shift()
    )


    tr = pd.concat(
        [
            tr1,
            tr2,
            tr3
        ],
        axis=1
    ).max(axis=1)


    atr = tr.rolling(period).mean()


    plus_di = (
        100 *
        plus_dm.rolling(period).mean()
        /
        atr
    )


    minus_di = (
        100 *
        minus_dm.rolling(period).mean()
        /
        atr
    )


    dx = (
        abs(plus_di - minus_di)
        /
        (plus_di + minus_di)
    ) * 100


    return dx.rolling(period).mean()



def indicators(df):

    data = df.copy()


    data["Williams_R"] = williams_r(data)

    data["SMA14"] = sma(data)

    data["EMA14"] = ema(data)

    data["RSI14"] = rsi(data)

    data["MACD"] = macd(data)

    data["ADX14"] = adx(data)


    data["Williams_signal"] = 0


    data.loc[
        data["Williams_R"] < -80,
        "Williams_signal"
    ] = 1


    data.loc[
        data["Williams_R"] > -20,
        "Williams_signal"
    ] = -1


    return data



def info():

    return (
        "Technical indicators: "
        "Williams %R, RSI, SMA, EMA, MACD, ADX"
    )