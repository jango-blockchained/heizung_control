"""Config flow for Climate Control integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.components import mqtt

from .const import (
    DOMAIN,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_TEMP_STEP,
    CONF_PRECISION,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_TEMP_STEP,
    DEFAULT_PRECISION,
    CONF_MODE_COMMAND_TOPIC,
    CONF_MODE_STATE_TOPIC,
    CONF_TEMPERATURE_COMMAND_TOPIC,
    CONF_TEMPERATURE_STATE_TOPIC,
    CONF_CURRENT_TEMPERATURE_TOPIC,
    CONF_POWER_COMMAND_TOPIC,
    CONF_POWER_STATE_TOPIC,
    CONF_FAN_MODE_COMMAND_TOPIC,
    CONF_FAN_MODE_STATE_TOPIC,
    ERROR_MQTT_UNAVAILABLE,
    ERROR_INVALID_TOPIC,
    ERROR_TOPIC_NOT_EXIST,
    HVAC_MODES,
    FAN_MODES,
)

class ClimateControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Climate Control."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def validate_mqtt_topics(self, topics: list[str]) -> bool:
        """Validate that MQTT topics exist and are accessible."""
        if not await mqtt.async_wait_for_mqtt_client(self.hass):
            return False
        
        for topic in topics:
            if not await mqtt.async_subscribe(self.hass, topic, None):
                return False
        return True

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Check if device already exists
                await self.async_set_unique_id(user_input[CONF_NAME])
                self._abort_if_unique_id_configured()

                # Check if MQTT integration is configured
                if not self.hass.config.components.get("mqtt"):
                    errors["base"] = ERROR_MQTT_UNAVAILABLE
                else:
                    # Validate MQTT topics
                    required_topics = [
                        user_input[CONF_MODE_COMMAND_TOPIC],
                        user_input[CONF_TEMPERATURE_COMMAND_TOPIC],
                        user_input[CONF_TEMPERATURE_STATE_TOPIC],
                        user_input[CONF_CURRENT_TEMPERATURE_TOPIC],
                    ]
                    if not await self.validate_mqtt_topics(required_topics):
                        errors["base"] = ERROR_TOPIC_NOT_EXIST
                    else:
                        self._data.update(user_input)
                        return await self.async_step_climate()
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_MODE_COMMAND_TOPIC): str,
                    vol.Required(CONF_MODE_STATE_TOPIC): str,
                    vol.Required(CONF_TEMPERATURE_COMMAND_TOPIC): str,
                    vol.Required(CONF_TEMPERATURE_STATE_TOPIC): str,
                    vol.Required(CONF_CURRENT_TEMPERATURE_TOPIC): str,
                    vol.Optional(CONF_POWER_COMMAND_TOPIC): str,
                    vol.Optional(CONF_POWER_STATE_TOPIC): str,
                    vol.Optional(CONF_FAN_MODE_COMMAND_TOPIC): str,
                    vol.Optional(CONF_FAN_MODE_STATE_TOPIC): str,
                }
            ),
            errors=errors,
        )

    async def async_step_climate(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle climate options step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate temperature ranges
                if user_input[CONF_MIN_TEMP] >= user_input[CONF_MAX_TEMP]:
                    errors[CONF_MIN_TEMP] = "min_temp_higher"
                elif user_input[CONF_TEMP_STEP] <= 0:
                    errors[CONF_TEMP_STEP] = "invalid_temp_step"
                elif user_input[CONF_PRECISION] <= 0:
                    errors[CONF_PRECISION] = "invalid_precision"
                else:
                    self._data.update(user_input)
                    return self.async_create_entry(
                        title=self._data[CONF_NAME],
                        data=self._data,
                    )
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="climate",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP): vol.Coerce(float),
                    vol.Required(CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP): vol.Coerce(float),
                    vol.Required(CONF_TEMP_STEP, default=DEFAULT_TEMP_STEP): vol.Coerce(float),
                    vol.Required(CONF_PRECISION, default=DEFAULT_PRECISION): vol.Coerce(float),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate temperature ranges
                if user_input[CONF_MIN_TEMP] >= user_input[CONF_MAX_TEMP]:
                    errors[CONF_MIN_TEMP] = "min_temp_higher"
                elif user_input[CONF_TEMP_STEP] <= 0:
                    errors[CONF_TEMP_STEP] = "invalid_temp_step"
                elif user_input[CONF_PRECISION] <= 0:
                    errors[CONF_PRECISION] = "invalid_precision"
                else:
                    return self.async_create_entry(title="", data=user_input)
            except Exception:
                errors["base"] = "unknown"

        options = {
            vol.Required(
                CONF_MIN_TEMP,
                default=self.config_entry.options.get(
                    CONF_MIN_TEMP, DEFAULT_MIN_TEMP
                ),
            ): vol.Coerce(float),
            vol.Required(
                CONF_MAX_TEMP,
                default=self.config_entry.options.get(
                    CONF_MAX_TEMP, DEFAULT_MAX_TEMP
                ),
            ): vol.Coerce(float),
            vol.Required(
                CONF_TEMP_STEP,
                default=self.config_entry.options.get(
                    CONF_TEMP_STEP, DEFAULT_TEMP_STEP
                ),
            ): vol.Coerce(float),
            vol.Required(
                CONF_PRECISION,
                default=self.config_entry.options.get(
                    CONF_PRECISION, DEFAULT_PRECISION
                ),
            ): vol.Coerce(float),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options),
            errors=errors,
        ) 