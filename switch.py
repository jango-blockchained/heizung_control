"""Switch platform for Climate Control."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components import mqtt

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

MQTT_STATE_TOPIC = "home/switch/climate/state"
MQTT_COMMAND_TOPIC = "home/switch/climate/set"

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Climate switch."""
    add_entities([ClimateSwitch(hass)])

class ClimateSwitch(SwitchEntity):
    """Representation of a Climate switch."""

    _attr_name = "Climate"
    _attr_unique_id = "climate_switch"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the switch."""
        self.hass = hass
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events."""
        await mqtt.async_subscribe(
            self.hass,
            MQTT_STATE_TOPIC,
            self._mqtt_message_received,
            1
        )

    @callback
    def _mqtt_message_received(self, message):
        """Handle new MQTT messages."""
        payload = message.payload
        self._attr_is_on = payload == "ON"
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await mqtt.async_publish(
            self.hass, MQTT_COMMAND_TOPIC, "ON"
        )
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await mqtt.async_publish(
            self.hass, MQTT_COMMAND_TOPIC, "OFF"
        )
        self._attr_is_on = False 