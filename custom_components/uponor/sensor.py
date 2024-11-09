from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Uponor temperature sensors."""
    state_proxy = hass.data[DOMAIN]["state_proxy"]

    temperature_sensors = []
    for thermostat in hass.data[DOMAIN]["thermostats"]:
        # Get room name
        if thermostat.lower() in entry.data:
            name = entry.data[thermostat.lower()]
        else:
            name = state_proxy.get_room_name(thermostat)

        # Create and add a temperature sensor for the room
        temperature_sensors.append(RoomCurrentTemperatureSensor(state_proxy, thermostat, name))

    # Add only temperature sensors as entities
    if temperature_sensors:
        async_add_entities(temperature_sensors, update_before_add=False)


class RoomCurrentTemperatureSensor(SensorEntity):
    """Representation of a temperature sensor for an Uponor room."""

    def __init__(self, state_proxy, room_id, room_name):
        """Initialize the sensor with Uponor data, room ID, and name."""
        self._state_proxy = state_proxy
        self._room_id = room_id
        self._attr_name = f"{room_name} Current Temperature"
        self._attr_unique_id = f"{DOMAIN}_{room_id}_current_temperature"
        self._attr_unit_of_measurement = TEMP_CELSIUS
        self._state = None

    @property
    def state(self):
        """Return the current temperature for the sensor."""
        return self._state

    async def async_update(self):
        """Update the sensor's data from the Uponor system."""
        # Get the current temperature for the room using the same method as in UponorClimate
        try:
            self._state = self._state_proxy.get_temperature(self._room_id)
            _LOGGER.debug(f"Updated temperature for {self._attr_name}: {self._state}")
        except Exception as e:
            _LOGGER.warning(f"Failed to retrieve temperature for room {self._attr_name}: {e}")
