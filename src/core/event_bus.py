class EventBus:


    def __init__(self):

        self.listeners = []



    def subscribe(self, listener):

        self.listeners.append(listener)



    def publish(self, snapshot):

        for listener in self.listeners:

            listener.on_bar(snapshot)