from src.storage.feature_store import FeatureStore


class StoreListener:
    """
    Получает события баров
    и сохраняет их в FeatureStore.
    """


    def __init__(self):

        self.store = FeatureStore()



    def on_bar(self, snapshot):

        self.store.save(snapshot)


    def get_store(self):

        return self.store