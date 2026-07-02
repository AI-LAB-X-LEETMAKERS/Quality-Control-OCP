#include "../include/qco.h"
#include "../include/motors.h"

state g_state = {};


void setup() {
	g_state.vibrator = {26, 27, 25, 0, 5000, 8, MOTOR_5V};
	g_state.cleaning = {32, 33, 35, 1, 5000, 8, MOTOR_12V};
	init_motor(&g_state.vibrator);
}

void loop() 
{
	motorRun(&g_state.vibrator, true, 100);
	delay(2000);
	motorRun(&g_state.vibrator, false, 70);
	delay(2000);
}