#pragma once
#include "qco.h"

void init_servo(t_servo *servo);
void turn_servo(t_servo *servo, int angle);
void handleServoJson(state *g_state, const char* json);
void handleServo(state *g_state);