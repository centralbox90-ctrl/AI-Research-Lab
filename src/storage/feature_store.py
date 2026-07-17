class FeatureStore:
    """
    Хранилище всех MarketSnapshot.

    Каждая свеча сохраняется
    как отдельное состояние рынка.
    """


    def __init__(self):

        self.snapshots = []


    def save(self, snapshot):

        self.snapshots.append(snapshot)



    def get_all(self):

        return self.snapshots



    def get_last(self):

        if len(self.snapshots) == 0:
            return None

        return self.snapshots[-1]



    def count(self):

        return len(self.snapshots)



    def find_by_bar_id(self, bar_id):

        for snapshot in self.snapshots:

            if snapshot.identity.bar_id == bar_id:

                return snapshot


        return None