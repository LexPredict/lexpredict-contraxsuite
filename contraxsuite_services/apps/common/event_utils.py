from typing import TypeVar, Set, Generic, Type, Callable

EventType = TypeVar('EventType')


class EventManager(Generic[EventType]):
    def __init__(self, _event_type: Type[EventType]):
        super().__init__()
        self.listeners = set()  # type: Set[Callable[[EventType], None]]

    def add_listener(self, l: Callable[[EventType], None]):
        self.listeners.add(l)

    def remove_listener(self, l: Callable[[EventType], None]):
        self.listeners.remove(l)

    def fire(self, event: EventType):
        for l in self.listeners:
            l(event)

    def __call__(self, *args, **kwargs):
        self.fire(*args, **kwargs)


ObjType = TypeVar('ObjType')


class ObjectDeletedEvent(Generic[ObjType]):
    __slots__ = ['obj']

    def __init__(self, obj: ObjType) -> None:
        super().__init__()
        self.obj = obj


class ObjectChangedEvent(Generic[ObjType]):
    __slots__ = ['obj']

    def __init__(self, obj: ObjType) -> None:
        super().__init__()
        self.obj = obj
