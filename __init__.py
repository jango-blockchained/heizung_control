"""The Heizung Control integration."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import Platform

from .automation import setup_automations

DOMAIN = "heizung_control"
_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SWITCH, Platform.GROUP]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Heizung Control component."""
    hass.data[DOMAIN] = {}
    
    await hass.helpers.discovery.async_load_platform(
        "binary_sensor", DOMAIN, {}, config
    )
    await hass.helpers.discovery.async_load_platform(
        "switch", DOMAIN, {}, config
    )
    
    # Set up automations
    await setup_automations(hass)
    
    return True 