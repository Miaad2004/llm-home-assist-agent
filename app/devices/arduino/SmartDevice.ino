/*
  SmartDevice.ino - Main Arduino sketch for Smart Home Assistant integration
  Handles serial commands for device control and sensor reading.
*/
#include <Arduino.h>
#include "helpers.h"

void setup()
{
    Serial.begin(9600);
    pinMode(RELAY_PIN, OUTPUT);
    pinMode(SENSOR_PIN, INPUT);
    digitalWrite(RELAY_PIN, LOW);
}

void loop()
{
    if (Serial.available())
    {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd == "SET LIGHT ON")
        {
            toggleRelay(true);
            Serial.println("OK LIGHT ON");
        }
        else if (cmd == "SET LIGHT OFF")
        {
            toggleRelay(false);
            Serial.println("OK LIGHT OFF");
        }
        else if (cmd == "GET TEMP")
        {
            int value = analogRead(SENSOR_PIN);
            Serial.print("TEMP ");
            Serial.println(value);
        }
        else
        {
            Serial.println("ERR UNKNOWN");
        }
    }
}
