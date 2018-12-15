from collections import defaultdict
from aio_pubsub.interfaces import PubSub, Subscriber
from queue import Queue
from weakref import WeakSet


class MemorySubscriber(Subscriber):
    def __init__(self, queue_factory):
        self.messages = queue_factory(maxsize=0)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return self.messages.get()

    async def put(self, message):
        self.messages.put_nowait(message)


class MemoryPubSub(PubSub):
    def __init__(self, queue_factory=Queue):
        self.subscribers = defaultdict(WeakSet)
        self.queue_factory = queue_factory

    async def publish(self, channel, message):
        subscribers = self.subscribers[channel]
        for subscriber in subscribers:
            await subscriber.put(message)
        return len(subscribers)

    async def subscribe(self, channel):
        subscriber = MemorySubscriber(self.queue_factory)
        self.subscribers[channel].add(subscriber)
        return subscriber