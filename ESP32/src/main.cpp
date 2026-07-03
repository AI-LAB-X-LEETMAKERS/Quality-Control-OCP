#include "../include/qco.h"
#include "../include/motors.h"
#include "../include/servo.h"

state g_state = {};

void setup() {
	g_state.vibrator = {26, 27, 25, 0, 5000, 8, MOTOR_5V};
	g_state.cleaning = {18, 19, 21, 1, 5000, 8, MOTOR_12V};
	g_state.port = {33, 0};
	g_state.lock = {17, 0};
	init_motor(&g_state.vibrator);
	init_motor(&g_state.cleaning);
	init_servo(&g_state.port);
	init_servo(&g_state.lock);
}


void loop() 
{
	const char* testJson = R"({
        "motors": {
            "vibrator": { "speed": 100, "forward": true },
            "cleaning": { "speed": 100, "forward": true }
        },
		"servos": {
			"lock": { "angle": 0 },
			"door": { "angle": 0 }
		}
    })";

    handleServoJson(&g_state, testJson);
	delay(2000);

	const char* testJson2 = R"({
        "motors": {
            "vibrator": { "speed": 100, "forward": true },
            "cleaning": { "speed": 100, "forward": true }
        },
		"servos": {
			"lock": { "angle": 90 },
			"door": { "angle": 90 }
		}
    })";
	handleServoJson(&g_state, testJson2);
	delay(2000);
} 