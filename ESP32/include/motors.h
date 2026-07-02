#pragma once
#include "qco.h"

void init_motor(t_motor *motor);
void motorRun(t_motor *motor, bool forward, int speed);