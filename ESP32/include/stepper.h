#pragma once
#include "qco.h"

void init_stepper(t_stepper *stepper);
void stepperRun(t_stepper *stepper);
void handleStepperJson(state *g_state, const char* json);
void handleStepper(state *g_state);