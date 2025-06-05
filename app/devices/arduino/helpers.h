// helpers.h - Shared definitions and helper functions for Arduino SmartDevice
#ifndef HELPERS_H
#define HELPERS_H

// Example: Pin definitions
#define RELAY_PIN 8
#define SENSOR_PIN A0

// Example: Helper function
void toggleRelay(bool on)
{
    digitalWrite(RELAY_PIN, on ? HIGH : LOW);
}

#endif // HELPERS_H
