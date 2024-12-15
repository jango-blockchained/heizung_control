"""Automation handling for Climate Control."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import STATE_ON


async def setup_automations(hass: HomeAssistant) -> None:
    """Set up the automations for Climate Control."""
    
    async def handle_binary_sensor_change(entity_id, old_state, new_state):
        """Handle changes to the binary sensor state."""
        if new_state is None:
            return

        if new_state.state == STATE_ON:
            await hass.services.async_call(
                "switch", "turn_on", {"entity_id": "switch.climate"}
            )
        else:
            await hass.services.async_call(
                "switch", "turn_off", {"entity_id": "switch.climate"}
            )

    async_track_state_change(
        hass,
        "binary_sensor.climate_active",
        handle_binary_sensor_change
    ) 