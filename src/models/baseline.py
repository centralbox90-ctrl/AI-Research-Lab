from sklearn.linear_model import LogisticRegression
import pandas as pd


class BaselineModel:

    def __init__(self):

        self.features = [
            "momentum",
            "trend",
            "volatility",
            "market_signal"
        ]

        self.model = LogisticRegression()


    def train(self, data):

        df = data.copy()

        df = df.dropna()


        X = df[self.features]


        # цель:
        # если следующий бар выше -> рост

        y = (
            df["Close"]
            .shift(-1)
            >
            df["Close"]
        ).astype(int)


        y = y[:-1]
        X = X[:-1]


        self.model.fit(
            X,
            y
        )


    def predict(self, data):

        df = data.copy()

        X = df[self.features]


        prediction = self.model.predict(X)


        return pd.Series(
            prediction,
            index=df.index
        )