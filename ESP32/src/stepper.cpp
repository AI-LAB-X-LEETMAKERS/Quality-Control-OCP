#include "../include/stepper.h"

void init_stepper(t_stepper *stepper)
{
    pinMode(stepper->pinDir, OUTPUT);
    pinMode(stepper->pinStep, OUTPUT);

    digitalWrite(stepper->pinDir, LOW);
    digitalWrite(stepper->pinStep, LOW);

    stepper->lastStepTime = 0;
    stepper->stepState = LOW;
}

void stepperRun(t_stepper *stepper)
{
    if (stepper->speed == 0)
        return;

    int delayUs = map(stepper->speed, 1, 100, stepper->maxDelayUs, stepper->minDelayUs);

    digitalWrite(stepper->pinDir, stepper->forward ? HIGH : LOW);

    unsigned long now = micros();
    if (now - stepper->lastStepTime >= (unsigned long)delayUs) {
        stepper->stepState = !stepper->stepState;
        digitalWrite(stepper->pinStep, stepper->stepState);
        stepper->lastStepTime = now;
    }
}

void handleStepperJson(state *g_state, const char* json)
{
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, json);

    if (error) {
        Serial.print("JSON parse failed: ");
        Serial.println(error.c_str());
        return;
    }

    JsonObject steppers = doc["steppers"];

    if (steppers["cleaning"].is<JsonObject>()) {
        int speed = steppers["cleaning"]["speed"];
        bool forward = steppers["cleaning"]["forward"];
        g_state->cleaning.forward = forward;
        g_state->cleaning.speed = speed;
    } 
}

void handleStepper(state *g_state)
{
    stepperRun(&g_state->cleaning);
}