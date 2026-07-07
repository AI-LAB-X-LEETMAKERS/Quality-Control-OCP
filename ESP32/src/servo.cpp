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

    // Port
    if (doc["port"].is<JsonObject>()) {
        int angle = doc["port"]["angle"] | 0;

        Serial.printf("Set port angle to %d\n", angle);

        g_state->port.angle = angle;
    }

    // Lock
    if (doc["lock"].is<JsonObject>()) {
        int angle = doc["lock"]["angle"] | 0;

        Serial.printf("Set lock angle to %d\n", angle);

        g_state->lock.angle = angle;
    }
}

void handleServo(state *g_state)
{
	turn_servo(&g_state->lock, g_state->lock.angle);
	turn_servo(&g_state->port, g_state->port.angle);
}