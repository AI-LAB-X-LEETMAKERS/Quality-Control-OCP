#include "../include/motors.h"


void init_motor(t_motor *motor)
{
	pinMode(motor->pinForward, OUTPUT);
	pinMode(motor->pinReverse, OUTPUT);
	ledcSetup(motor->pwmChannel, motor->pwmFreq, motor->pwmResolution);
	ledcAttachPin(motor->pinEnable, motor->pwmChannel);
	digitalWrite(motor->pinForward, LOW);
	digitalWrite(motor->pinReverse, LOW);
}

void motorRun(t_motor *motor, bool forward, int speedPercent)
{
    speedPercent = constrain(speedPercent, 0, 100);

	if (speedPercent == 0)
	{
		digitalWrite(motor->pinForward, LOW);
    	digitalWrite(motor->pinReverse, LOW);
		return ;
	}

    int pwmCeiling;
    if (motor->type == MOTOR_5V)
        pwmCeiling = 130;
    else
        pwmCeiling = 255;

    int pwmValue = map(speedPercent, 0, 100, 0, pwmCeiling);

    digitalWrite(motor->pinForward, forward ? HIGH : LOW);
    digitalWrite(motor->pinReverse, forward ? LOW : HIGH);
    ledcWrite(motor->pwmChannel, pwmValue);
}

void handleMotorJson(state *g_state, const char* json)
{
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, json);

    if (error) {
        Serial.print("JSON parse failed: ");
        Serial.println(error.c_str());
        return;
    }

    JsonObject motors = doc["motors"];

    // Vibrator
    if (motors["vibrator"].is<JsonObject>()) {
        int speed = motors["vibrator"]["speed"];
        bool forward = motors["vibrator"]["forward"];
        g_state->vibrator.forward = forward;
        g_state->vibrator.speed = speed;
    }

    // Cleaning
    if (motors["cleaning"].is<JsonObject>()) {
        int speed = motors["cleaning"]["speed"];
        bool forward = motors["cleaning"]["forward"];
        g_state->cleaning.forward = forward;
        g_state->cleaning.speed = speed;
    }
}

void handleMotor(state *g_state)
{
	 motorRun(&g_state->cleaning, g_state->cleaning.forward, g_state->cleaning.speed);
	 motorRun(&g_state->vibrator, g_state->vibrator.forward, g_state->vibrator.speed);
}