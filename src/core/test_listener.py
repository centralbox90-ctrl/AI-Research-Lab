class TestListener:


    def on_bar(self, snapshot):

        print(
            "Получен бар:",
            snapshot.identity.bar_id
        )