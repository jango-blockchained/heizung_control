# Heizung Control Integration for Home Assistant

This custom integration manages heating control by monitoring a group of climate entities and controlling an MQTT switch based on their state.

## Features

- Creates a binary sensor that monitors a group of climate entities
- Controls an MQTT switch based on the binary sensor state
- Automatically turns the switch on/off when any climate device becomes active/inactive

## Installation

1. Copy the `heizung_control` folder to your `custom_components` directory
2. Restart Home Assistant
3. The integration will automatically set up the following entities:
   - `binary_sensor.heizung_active`: Indicates if any climate device is active
   - `switch.heizung`: MQTT switch that controls the heating system

## Configuration

The integration uses the following MQTT topics:
- State Topic: `home/switch/heizung/state`
- Command Topic: `home/switch/heizung/set`

The integration expects the following climate entities to be available in a group:
- `climate.heizung_links_wohnzimmer`
- `climate.heizung_rechts_wohnzimmer`
- `climate.heizung_küche`

## How it Works

1. The binary sensor monitors the state of all climate entities in the group
2. When any climate device becomes active (not 'off' or 'idle'), the binary sensor turns on
3. The automation watches the binary sensor and controls the MQTT switch accordingly
4. The MQTT switch can also be controlled manually through the Home Assistant interface

## Requirements

- Home Assistant
- MQTT integration set up and configured
- Climate entities configured and working 