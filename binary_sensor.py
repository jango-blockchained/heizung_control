"""Binary sensor platform for Heizung Control."""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import STATE_ON, STATE_OFF

from . import DOMAIN

CLIMATE_GROUP = "group.heizung_climates"

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Heizung binary sensor."""
    add_entities([HeizungActiveSensor(hass)])

class HeizungActiveSensor(BinarySensorEntity):
    """Binary sensor that monitors if any climate device is active."""

    _attr_name = "Heizung Active"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_unique_id = "heizung_active_sensor"
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Handle added to Hass."""
        self.async_schedule_update_ha_state(True)
        
        # Track state changes for all climate entities in the group
        group_state = self.hass.states.get(CLIMATE_GROUP)
        if group_state:
            climate_entities = group_state.attributes.get("entity_id", [])
            async_track_state_change(
                self.hass, climate_entities, self._handle_climate_state_change
            )

    async def _handle_climate_state_change(self, entity_id, old_state, new_state):
        """Handle climate state changes."""
        await self.async_update()

    async def async_update(self) -> None:
        """Update the sensor state."""
        group_state = self.hass.states.get(CLIMATE_GROUP)
        if not group_state:
            self._attr_is_on = False
            return

        climate_entities = group_state.attributes.get("entity_id", [])
        active_climates = []

        for entity_id in climate_entities:
            state = self.hass.states.get(entity_id)
            if state and state.state not in ["off", "idle"]:
                active_climates.append(entity_id)

        self._attr_is_on = len(active_climates) > 0 