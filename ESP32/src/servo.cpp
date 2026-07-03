#include "../include/servo.h"

void init_servo(t_servo *servo)
{
	servo->servo.attach(servo->pin);	
}

void turn_servo(t_servo *servo, int angle)
{
	servo->servo.write(angle);
}

void handleServoJson(state *g_state, const char* json)
{
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, json);

    if (error) {
        Serial.print("JSON parse failed: ");
        Serial.println(error.c_str());
        return;
    }

    JsonObject servos = doc["servos"];

    // Port
    if (servos["port"].is<JsonObject>()) {
        int angle = servos["port"]["angle"];
        turn_servo(&g_state->port, angle);
    }

    // Lock
    if (servos["lock"].is<JsonObject>()) {
        int angle = servos["lock"]["angle"];
        turn_servo(&g_state->lock, angle);
    }
}
