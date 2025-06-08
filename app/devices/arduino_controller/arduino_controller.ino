/*
 * Arduino Controller for Smart Home Assistant
 *
 * This sketch reads commands from the serial port in the format:
 * PIN:VALUE\n
 * Where:
 *   PIN is the digital pin number (e.g., 5, 6, 7)
 *   VALUE is 1 for HIGH (on) or 0 for LOW (off)
 *
 * Example: "5:1\n" will set pin 5 HIGH (on)
 *          "6:0\n" will set pin 6 LOW (off)
 *
 * The Arduino responds with "OK" if successful, or "ERROR" if the command is invalid.
 */

const int maxPins = 13; // Maximum number of pins to control (adjust as needed)

void setup()
{
    Serial.begin(9600);

    // Initialize all pins as OUTPUT
    for (int i = 2; i <= maxPins; i++)
    {
        pinMode(i, OUTPUT);
        digitalWrite(i, HIGH); // Start with everything off
    }

    Serial.println("Arduino Ready");
}

void loop()
{
    if (Serial.available())
    {
        String command = Serial.readStringUntil('\n');

        // Parse command (PIN:VALUE)
        int separatorIndex = command.indexOf(':');
        if (separatorIndex > 0)
        {
            int pin = command.substring(0, separatorIndex).toInt();
            int value = command.substring(separatorIndex + 1).toInt();

            // Validate pin number
            if (pin >= 2 && pin <= maxPins)
            {
                // Set pin state
                digitalWrite(pin, value == 1 ? LOW : HIGH);
                Serial.println("OK");
            }
            else
            {
                Serial.println("ERROR:INVALID_PIN");
            }
        }
        else
        {
            Serial.println("ERROR:INVALID_COMMAND");
        }
    }

    // Small delay to not overload the serial buffer
    delay(10);
}
