#include <Arduino.h>
#include <ArduinoJson.h>

// Pin definitions
#define BEDROOM_LIGHT_PIN 5
#define IR_LED_PIN 6

// --- Device Base Class ---
class Device
{
public:
    virtual bool handleAction(const char *action, JsonObject args, JsonObject response) = 0;
};

// --- Bedroom Light Device ---
class BedroomLight : public Device
{
public:
    BedroomLight(uint8_t pin) : pin(pin), brightness(100)
    {
        pinMode(pin, OUTPUT);
        analogWrite(pin, 255); // Default ON
    }

    bool handleAction(const char *action, JsonObject args, JsonObject response) override
    {
        if (strcmp(action, "turn_on") == 0)
        {
            analogWrite(pin, map(brightness, 0, 100, 0, 255));
            response["msg"] = "Bedroom light turned on";
            return true;
        }
        if (strcmp(action, "turn_off") == 0)
        {
            analogWrite(pin, 0);
            response["msg"] = "Bedroom light turned off";
            return true;
        }
        if (strcmp(action, "set_brightness") == 0)
        {
            if (!args.containsKey("level"))
            {
                response["msg"] = "Missing required argument: level";
                return false;
            }
            int level = args["level"];
            if (level < 0 || level > 100)
            {
                response["msg"] = "Brightness out of range (0-100)";
                return false;
            }
            brightness = level;
            analogWrite(pin, map(brightness, 0, 100, 0, 255));
            response["msg"] = "Brightness set";
            return true;
        }
        response["msg"] = "Unknown action";
        return false;
    }

private:
    uint8_t pin;
    int brightness;
};

// --- IR LED Device ---
class IrLed : public Device
{
public:
    IrLed(uint8_t pin) : pin(pin)
    {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, LOW);
    }

    bool handleAction(const char *action, JsonObject args, JsonObject response) override
    {
        if (strcmp(action, "send_code") == 0)
        {
            if (!args.containsKey("code"))
            {
                response["msg"] = "Missing required argument: code";
                return false;
            }
            // For demonstration, just blink the IR LED
            digitalWrite(pin, HIGH);
            delay(100);
            digitalWrite(pin, LOW);
            response["msg"] = "IR code sent (simulated)";
            return true;
        }
        response["msg"] = "Unknown action";
        return false;
    }

private:
    uint8_t pin;
};

// --- Device Registry ---
struct DeviceEntry
{
    const char *id;
    Device *device;
};

BedroomLight bedroomLight(BEDROOM_LIGHT_PIN);
IrLed irLed(IR_LED_PIN);

DeviceEntry devices[] = {
    {"bedroom_light", &bedroomLight},
    {"ir_led", &irLed}};
const size_t deviceCount = sizeof(devices) / sizeof(devices[0]);

Device *findDevice(const char *id)
{
    for (size_t i = 0; i < deviceCount; ++i)
    {
        if (strcmp(devices[i].id, id) == 0)
            return devices[i].device;
    }
    return nullptr;
}

// --- Serial JSON Handling ---
String inputLine;

void sendResponse(JsonObject response)
{
    serializeJson(response, Serial);
    Serial.println();
}

void processCommand(const char *json)
{
    StaticJsonDocument<256> doc;
    JsonObject response;
    StaticJsonDocument<128> respDoc;
    response = respDoc.to<JsonObject>();
    response["code"] = 1; // Default: error

    DeserializationError err = deserializeJson(doc, json);
    if (err)
    {
        response["msg"] = "Malformed JSON";
        sendResponse(response);
        return;
    }

    // Required fields
    if (!doc.containsKey("id") || !doc.containsKey("device_id") || !doc.containsKey("action"))
    {
        response["msg"] = "Missing required fields";
        sendResponse(response);
        return;
    }

    response["id"] = doc["id"];

    const char *device_id = doc["device_id"];
    const char *action = doc["action"];
    JsonObject args = doc.containsKey("args") ? doc["args"].as<JsonObject>() : JsonObject();

    Device *device = findDevice(device_id);
    if (!device)
    {
        response["msg"] = "Unknown device_id";
        sendResponse(response);
        return;
    }

    bool ok = device->handleAction(action, args, response);
    response["code"] = ok ? 0 : 2;
    sendResponse(response);
}

void setup()
{
    Serial.begin(9600);
}

void loop()
{
    while (Serial.available())
    {
        char c = Serial.read();
        if (c == '\n' || c == '\r')
        {
            if (inputLine.length() > 0)
            {
                processCommand(inputLine.c_str());
                inputLine = "";
            }
        }
        else
        {
            inputLine += c;
        }
    }
}