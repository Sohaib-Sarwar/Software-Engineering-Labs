"""
design_patterns.py
===================

Clean, minimal, standard-library-only implementations of three classic
design patterns:

1. **Singleton** -- ``ConfigurationManager`` guarantees a single shared
   instance exists for the lifetime of the process.
2. **Factory Method** -- ``NotificationFactory`` subclasses decide *which*
   concrete ``Notification`` product to build, without the calling code
   ever needing to know the concrete class name.
3. **Observer** -- ``WeatherStation`` (the subject) notifies any number of
   registered ``Observer`` objects whenever its measurements change,
   without being coupled to what those observers do with the data.

Each pattern has a short, runnable demonstration under the
``if __name__ == "__main__":`` guard at the bottom of the file, so running

    python source/design_patterns.py

prints a small trace showing each pattern in action.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List


# ===========================================================================
# 1. Singleton
# ===========================================================================

class ConfigurationManager:
    """A process-wide configuration store.

    The Singleton pattern is appropriate here because application
    configuration should have exactly one source of truth: creating a
    second, independent instance would risk different parts of the program
    disagreeing about the current settings.

    Implementation notes:

    * ``__new__`` is overridden (rather than relying on module-level state)
      so the guarantee lives on the class itself and survives being
      imported from multiple places.
    * ``__init__`` runs every time ``ConfigurationManager()`` is called, so
      it is guarded to only populate defaults on the *first* construction;
      subsequent calls return the same object without resetting its state.
    """

    _instance: "ConfigurationManager | None" = None

    def __new__(cls) -> "ConfigurationManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._settings: Dict[str, str] = {
            "environment": "development",
            "log_level": "INFO",
        }
        self._initialized = True

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._settings.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._settings[key] = value

    def as_dict(self) -> Dict[str, str]:
        return dict(self._settings)

    @classmethod
    def _reset_for_testing(cls) -> None:
        """Clear the singleton instance. Intended for use by unit tests only."""
        cls._instance = None


# ===========================================================================
# 2. Factory Method
# ===========================================================================

class Notification(ABC):
    """Product interface: something that can render itself as a message."""

    @abstractmethod
    def render(self, recipient: str, message: str) -> str:
        raise NotImplementedError


class EmailNotification(Notification):
    def render(self, recipient: str, message: str) -> str:
        return f"[Email to {recipient}] {message}"


class SmsNotification(Notification):
    def render(self, recipient: str, message: str) -> str:
        return f"[SMS to {recipient}] {message}"


class PushNotification(Notification):
    def render(self, recipient: str, message: str) -> str:
        return f"[Push to {recipient}] {message}"


class NotificationFactory(ABC):
    """Creator interface declaring the factory method.

    Client code depends only on this abstract interface and on
    ``Notification``; it never names a concrete product class. Adding a new
    channel (e.g. a future ``SlackNotificationFactory``) requires no changes
    to any existing factory or client code -- only a new subclass.
    """

    @abstractmethod
    def create_notification(self) -> Notification:
        raise NotImplementedError

    def send(self, recipient: str, message: str) -> str:
        """Template method built on top of the factory method.

        This is the payoff of the pattern: ``send`` is written once, here,
        against the abstract ``Notification`` product, yet its concrete
        behaviour changes completely depending on which factory subclass is
        used to invoke it.
        """
        notification = self.create_notification()
        return notification.render(recipient, message)


class EmailNotificationFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return EmailNotification()


class SmsNotificationFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return SmsNotification()


class PushNotificationFactory(NotificationFactory):
    def create_notification(self) -> Notification:
        return PushNotification()


_FACTORY_REGISTRY: Dict[str, type] = {
    "email": EmailNotificationFactory,
    "sms": SmsNotificationFactory,
    "push": PushNotificationFactory,
}


def get_notification_factory(channel: str) -> NotificationFactory:
    """Convenience lookup so callers can select a factory by name.

    Raises ``ValueError`` for an unknown channel rather than silently
    returning ``None``, keeping failures loud and early.
    """
    try:
        factory_cls = _FACTORY_REGISTRY[channel]
    except KeyError:
        valid = ", ".join(sorted(_FACTORY_REGISTRY))
        raise ValueError(f"Unknown channel {channel!r}; expected one of: {valid}") from None
    return factory_cls()


# ===========================================================================
# 3. Observer
# ===========================================================================

class Observer(ABC):
    """Observer interface: anything that can react to a subject's update."""

    @abstractmethod
    def update(self, temperature_celsius: float, humidity_percent: float) -> None:
        raise NotImplementedError


class WeatherStation:
    """Subject: holds the current measurements and notifies observers of
    changes.

    The station knows nothing about *what* its observers do with a new
    reading -- it only knows it must call ``update`` on each of them. This
    decouples the measurement source from any number of independently
    varying displays/loggers/alerts.
    """

    def __init__(self) -> None:
        self._observers: List[Observer] = []
        self._temperature_celsius: float = 0.0
        self._humidity_percent: float = 0.0

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    @property
    def observer_count(self) -> int:
        return len(self._observers)

    def set_measurements(self, temperature_celsius: float, humidity_percent: float) -> None:
        self._temperature_celsius = temperature_celsius
        self._humidity_percent = humidity_percent
        self._notify_observers()

    def _notify_observers(self) -> None:
        for observer in list(self._observers):
            observer.update(self._temperature_celsius, self._humidity_percent)


class CurrentConditionsDisplay(Observer):
    """A concrete observer that keeps only the latest reading."""

    def __init__(self) -> None:
        self.last_temperature: float | None = None
        self.last_humidity: float | None = None

    def update(self, temperature_celsius: float, humidity_percent: float) -> None:
        self.last_temperature = temperature_celsius
        self.last_humidity = humidity_percent

    def render(self) -> str:
        return f"Now: {self.last_temperature}C, {self.last_humidity}% humidity"


class TemperatureAlertObserver(Observer):
    """A concrete observer that records every reading above a threshold."""

    def __init__(self, threshold_celsius: float) -> None:
        self._threshold_celsius = threshold_celsius
        self.alerts: List[float] = []

    def update(self, temperature_celsius: float, humidity_percent: float) -> None:
        if temperature_celsius > self._threshold_celsius:
            self.alerts.append(temperature_celsius)


class MeasurementLogger(Observer):
    """A concrete observer that accumulates a full history of readings."""

    def __init__(self) -> None:
        self.history: List[tuple] = []

    def update(self, temperature_celsius: float, humidity_percent: float) -> None:
        self.history.append((temperature_celsius, humidity_percent))


# ===========================================================================
# Demonstrations
# ===========================================================================

def _demo_singleton() -> None:
    print("--- Singleton ---")
    config_a = ConfigurationManager()
    config_b = ConfigurationManager()
    print("config_a is config_b:", config_a is config_b)
    config_a.set("log_level", "DEBUG")
    print("config_b sees the change too:", config_b.get("log_level"))


def _demo_factory_method() -> None:
    print("--- Factory Method ---")
    for channel in ("email", "sms", "push"):
        factory = get_notification_factory(channel)
        print(factory.send("alice", "Your order has shipped."))


def _demo_observer() -> None:
    print("--- Observer ---")
    station = WeatherStation()
    display = CurrentConditionsDisplay()
    alerts = TemperatureAlertObserver(threshold_celsius=30.0)
    logger = MeasurementLogger()

    station.attach(display)
    station.attach(alerts)
    station.attach(logger)

    station.set_measurements(22.5, 55.0)
    station.set_measurements(31.0, 40.0)

    print(display.render())
    print("High-temperature alerts recorded:", alerts.alerts)
    print("Full reading history:", logger.history)


if __name__ == "__main__":
    _demo_singleton()
    print()
    _demo_factory_method()
    print()
    _demo_observer()
