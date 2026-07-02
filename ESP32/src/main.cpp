#include "../include/qco.h"
#include "../include/motors.h"

state g_state = {};

void setup() {
	g_state.vibrator = {26, 27, 25, 0, 5000, 8, MOTOR_5V};
	g_state.cleaning = {32, 33, 35, 1, 5000, 8, MOTOR_12V};
	init_motor(&g_state.vibrator);
	init_motor(&g_state.cleaning);

}

void loop() 
{
	const char* testJson = R"({
        "motors": {
            "vibrator": { "speed": 100, "forward": true },
            "cleaning": { "speed": 0, "forward": false }
        }
    })";

    handleMotorJson(&g_state, testJson);
	delay(2000);

	const char *testJson2 = R"({
        "motors": {
            "vibrator": { "speed": 100, "forward": false },
            "cleaning": { "speed": 0, "forward": false }
        }
    })";
	handleMotorJson(&g_state, testJson2);
	delay(2000);
}