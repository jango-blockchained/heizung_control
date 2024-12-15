"""Automation handling for Heizung Control."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import STATE_ON, STATE_OFF

async def setup_automations(hass: HomeAssistant) -> None:
    """Set up the automations for Heizung Control."""
    
    async def handle_binary_sensor_change(entity_id, old_state, new_state):
        """Handle changes to the binary sensor state."""
        if new_state is None:
            return

        if new_state.state == STATE_ON:
            await hass.services.async_call(
                "switch", "turn_on", {"entity_id": "switch.heizung"}
            )
        else:
            await hass.services.async_call(
                "switch", "turn_off", {"entity_id": "switch.heizung"}
            )

    async_track_state_change(
        hass,
        "binary_sensor.heizung_active",
        handle_binary_sensor_change
    ) 