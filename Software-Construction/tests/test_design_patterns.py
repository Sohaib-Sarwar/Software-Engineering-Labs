"""
Unit tests for source/design_patterns.py.

Written against the standard library's ``unittest`` so they run with either

    python -m unittest discover tests

or, if pytest happens to be installed, simply

    pytest tests/test_design_patterns.py
"""

import os
import sys
import unittest

# Make the sibling "source" package importable regardless of the current
# working directory the test runner was invoked from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from source.design_patterns import (
    ConfigurationManager,
    CurrentConditionsDisplay,
    EmailNotification,
    EmailNotificationFactory,
    MeasurementLogger,
    PushNotification,
    PushNotificationFactory,
    SmsNotification,
    SmsNotificationFactory,
    TemperatureAlertObserver,
    WeatherStation,
    get_notification_factory,
)


class SingletonTests(unittest.TestCase):
    def tearDown(self):
        # Each test should start from a clean singleton so tests cannot leak
        # state into one another via the shared class attribute.
        ConfigurationManager._reset_for_testing()

    def test_repeated_construction_returns_the_same_instance(self):
        first = ConfigurationManager()
        second = ConfigurationManager()
        self.assertIs(first, second)

    def test_state_mutated_through_one_reference_is_visible_via_another(self):
        first = ConfigurationManager()
        second = ConfigurationManager()
        first.set("log_level", "DEBUG")
        self.assertEqual(second.get("log_level"), "DEBUG")

    def test_default_settings_present_on_first_construction(self):
        config = ConfigurationManager()
        self.assertEqual(config.get("environment"), "development")
        self.assertEqual(config.get("log_level"), "INFO")

    def test_get_with_missing_key_returns_default(self):
        config = ConfigurationManager()
        self.assertIsNone(config.get("does_not_exist"))
        self.assertEqual(config.get("does_not_exist", "fallback"), "fallback")

    def test_reset_for_testing_produces_a_genuinely_new_instance(self):
        first = ConfigurationManager()
        first.set("log_level", "DEBUG")
        ConfigurationManager._reset_for_testing()
        second = ConfigurationManager()
        self.assertIsNot(first, second)
        self.assertEqual(second.get("log_level"), "INFO")  # back to the default


class FactoryMethodTests(unittest.TestCase):
    def test_email_factory_builds_email_notification(self):
        factory = EmailNotificationFactory()
        notification = factory.create_notification()
        self.assertIsInstance(notification, EmailNotification)

    def test_sms_factory_builds_sms_notification(self):
        factory = SmsNotificationFactory()
        notification = factory.create_notification()
        self.assertIsInstance(notification, SmsNotification)

    def test_push_factory_builds_push_notification(self):
        factory = PushNotificationFactory()
        notification = factory.create_notification()
        self.assertIsInstance(notification, PushNotification)

    def test_template_method_send_uses_the_correct_product(self):
        factory = EmailNotificationFactory()
        rendered = factory.send("alice", "hello")
        self.assertEqual(rendered, "[Email to alice] hello")

    def test_get_notification_factory_by_name(self):
        self.assertIsInstance(get_notification_factory("email"), EmailNotificationFactory)
        self.assertIsInstance(get_notification_factory("sms"), SmsNotificationFactory)
        self.assertIsInstance(get_notification_factory("push"), PushNotificationFactory)

    def test_get_notification_factory_unknown_channel_raises(self):
        with self.assertRaises(ValueError):
            get_notification_factory("carrier-pigeon")

    def test_different_channels_produce_different_rendered_output(self):
        message = "Payment received"
        rendered_outputs = {
            channel: get_notification_factory(channel).send("bob", message)
            for channel in ("email", "sms", "push")
        }
        # Each channel must format its own distinct output for the same input.
        self.assertEqual(len(set(rendered_outputs.values())), 3)


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.station = WeatherStation()

    def test_attach_increases_observer_count(self):
        display = CurrentConditionsDisplay()
        self.station.attach(display)
        self.assertEqual(self.station.observer_count, 1)

    def test_attaching_the_same_observer_twice_does_not_duplicate(self):
        display = CurrentConditionsDisplay()
        self.station.attach(display)
        self.station.attach(display)
        self.assertEqual(self.station.observer_count, 1)

    def test_all_observers_receive_updates(self):
        display = CurrentConditionsDisplay()
        logger = MeasurementLogger()
        self.station.attach(display)
        self.station.attach(logger)

        self.station.set_measurements(21.0, 60.0)

        self.assertEqual(display.last_temperature, 21.0)
        self.assertEqual(display.last_humidity, 60.0)
        self.assertEqual(logger.history, [(21.0, 60.0)])

    def test_detach_stops_future_updates(self):
        display = CurrentConditionsDisplay()
        self.station.attach(display)
        self.station.set_measurements(20.0, 50.0)
        self.station.detach(display)
        self.station.set_measurements(99.0, 99.0)
        # The display must retain the last reading it saw before detaching.
        self.assertEqual(display.last_temperature, 20.0)
        self.assertEqual(self.station.observer_count, 0)

    def test_detaching_an_unattached_observer_is_a_no_op(self):
        display = CurrentConditionsDisplay()
        # Never attached; detaching should not raise.
        self.station.detach(display)
        self.assertEqual(self.station.observer_count, 0)

    def test_temperature_alert_only_fires_above_threshold(self):
        alerts = TemperatureAlertObserver(threshold_celsius=30.0)
        self.station.attach(alerts)

        self.station.set_measurements(25.0, 40.0)
        self.station.set_measurements(35.0, 40.0)
        self.station.set_measurements(30.0, 40.0)  # exactly at threshold: not "above"

        self.assertEqual(alerts.alerts, [35.0])

    def test_logger_accumulates_full_history_in_order(self):
        logger = MeasurementLogger()
        self.station.attach(logger)

        self.station.set_measurements(10.0, 10.0)
        self.station.set_measurements(20.0, 20.0)
        self.station.set_measurements(30.0, 30.0)

        self.assertEqual(
            logger.history,
            [(10.0, 10.0), (20.0, 20.0), (30.0, 30.0)],
        )


if __name__ == "__main__":
    unittest.main()
