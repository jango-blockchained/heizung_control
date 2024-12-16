"""Constants for the Climate Control integration."""
from typing import Final

DOMAIN: Final = "climate_control"
DEFAULT_NAME: Final = "Climate Control"

# Configuration Options
CONF_MIN_TEMP: Final = "min_temp"
CONF_MAX_TEMP: Final = "max_temp"
CONF_TEMP_STEP: Final = "temp_step"
CONF_PRECISION: Final = "precision"

# Default Values
DEFAULT_MIN_TEMP: Final = 7
DEFAULT_MAX_TEMP: Final = 35
DEFAULT_TEMP_STEP: Final = 0.5
DEFAULT_PRECISION: Final = 0.1

# MQTT Topics
CONF_MODE_COMMAND_TOPIC: Final = "mode_command_topic"
CONF_MODE_STATE_TOPIC: Final = "mode_state_topic"
CONF_TEMPERATURE_COMMAND_TOPIC: Final = "temperature_command_topic"
CONF_TEMPERATURE_STATE_TOPIC: Final = "temperature_state_topic"
CONF_CURRENT_TEMPERATURE_TOPIC: Final = "current_temperature_topic"
CONF_POWER_COMMAND_TOPIC: Final = "power_command_topic"
CONF_POWER_STATE_TOPIC: Final = "power_state_topic"
CONF_FAN_MODE_COMMAND_TOPIC: Final = "fan_mode_command_topic"
CONF_FAN_MODE_STATE_TOPIC: Final = "fan_mode_state_topic"

# MQTT Payloads
DEFAULT_PAYLOAD_ON: Final = "ON"
DEFAULT_PAYLOAD_OFF: Final = "OFF"

# Available modes
HVAC_MODES = ["off", "auto", "cool", "heat", "dry", "fan_only"]
FAN_MODES = ["auto", "low", "medium", "high"]

# Error messages
ERROR_MQTT_UNAVAILABLE: Final = "mqtt_unavailable"
ERROR_INVALID_TOPIC: Final = "invalid_topic"
ERROR_TOPIC_NOT_EXIST: Final = "topic_not_exist"