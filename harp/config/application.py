from dataclasses import asdict, is_dataclass
from typing import Optional

from whistle import IAsyncEventDispatcher

from harp.config.factories.events import EVENT_FACTORY_BIND, EVENT_FACTORY_BOUND


class Application:
    name = None

    settings_namespace = None
    settings_type = None

    on_bind = None
    """
    Placeholder for factory bind event, happening before the container is built. If set, it will be attached to the
    factory dispatcher automatically.

    """

    on_bound = None
    """
    Placeholder for factory bound event, happening after the container is built. If set, it will be attached to the
    factory dispatcher automatically.
    """

    def __init__(self, settings, /):
        if isinstance(settings, dict) and self.settings_type is not None:
            settings = self.settings_type(**settings)
        self.settings = settings

    @staticmethod
    def defaults(settings: Optional[dict] = None) -> dict:
        return {}

    @classmethod
    def supports(cls, settings: dict) -> bool:
        return True

    def validate(self):
        if is_dataclass(self.settings):
            return asdict(self.settings)
        return self.settings

    def register_events(self, dispatcher: IAsyncEventDispatcher):
        if self.on_bind is not None:
            dispatcher.add_listener(EVENT_FACTORY_BIND, self.on_bind)
        if self.on_bound is not None:
            dispatcher.add_listener(EVENT_FACTORY_BOUND, self.on_bound)

    def __repr__(self):
        return f'<{type(self).__name__} name="{self.name}">'