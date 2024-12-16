"""Platform for Climate Control integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.components.climate.const import ATTR_TEMPERATURE
from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_TEMP_STEP,
    CONF_PRECISION,
    CONF_MODE_COMMAND_TOPIC,
    CONF_MODE_STATE_TOPIC,
    CONF_TEMPERATURE_COMMAND_TOPIC,
    CONF_TEMPERATURE_STATE_TOPIC,
    CONF_CURRENT_TEMPERATURE_TOPIC,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_TEMP_STEP,
    DEFAULT_PRECISION,
    HVAC_MODES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Climate Control platform."""
    config = config_entry.data
    
    async_add_entities(
        [ClimateController(hass, config, config_entry.entry_id)],
        True,
    )


class ClimateController(ClimateEntity):
    """Representation of a Climate Control device."""

    _attr_has_entity_name = True
    _attr_name = None
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict[str, Any],
        entry_id: str,
    ) -> None:
        """Initialize the climate device."""
        self.hass = hass
        self._config = config
        self._attr_unique_id = entry_id
        
        # Temperature settings
        self._attr_min_temp = config.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP)
        self._attr_max_temp = config.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP)
        self._attr_target_temperature_step = config.get(
            CONF_TEMP_STEP, DEFAULT_TEMP_STEP
        )
        self._attr_precision = config.get(CONF_PRECISION, DEFAULT_PRECISION)
        
        # MQTT topics
        self._mode_command_topic = config[CONF_MODE_COMMAND_TOPIC]
        self._mode_state_topic = config[CONF_MODE_STATE_TOPIC]
        self._temp_command_topic = config[CONF_TEMPERATURE_COMMAND_TOPIC]
        self._temp_state_topic = config[CONF_TEMPERATURE_STATE_TOPIC]
        self._current_temp_topic = config[CONF_CURRENT_TEMPERATURE_TOPIC]
        
        # State
        self._attr_hvac_modes = HVAC_MODES
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_target_temperature = self.min_temp
        self._attr_current_temperature = None
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        
        # Features
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events."""
        await mqtt.async_subscribe(
            self.hass,
            self._mode_state_topic,
            self._handle_mode_state,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self._temp_state_topic,
            self._handle_temp_state,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self._current_temp_topic,
            self._handle_current_temp,
            1,
        )

    async def _handle_mode_state(self, msg):
        """Handle updates to the HVAC mode."""
        try:
            payload = msg.payload
            if payload in self.hvac_modes:
                self._attr_hvac_mode = payload
                self.async_write_ha_state()
        except Exception:
            _LOGGER.error("Could not handle mode state update")

    async def _handle_temp_state(self, msg):
        """Handle updates to the target temperature."""
        try:
            self._attr_target_temperature = float(msg.payload)
            self.async_write_ha_state()
        except ValueError:
            _LOGGER.error("Could not handle temperature state update")

    async def _handle_current_temp(self, msg):
        """Handle updates to the current temperature."""
        try:
            self._attr_current_temperature = float(msg.payload)
            self.async_write_ha_state()
        except ValueError:
            _LOGGER.error("Could not handle current temperature update")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await mqtt.async_publish(
            self.hass,
            self._temp_command_topic,
            temperature,
            0,
            False,
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode not in self.hvac_modes:
            _LOGGER.error("Unsupported HVAC mode: %s", hvac_mode)
            return

        await mqtt.async_publish(
            self.hass,
            self._mode_command_topic,
            hvac_mode,
            0,
            False,
        ) 