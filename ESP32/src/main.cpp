#include "../include/qco.h"
#include "../include/motors.h"
#include "../include/servo.h"

state g_state = {};

void setup() {
	Serial.begin(115200);

	g_state.vibrator = {26, 27, 25, 0, 5000, 8, MOTOR_5V, false, 0};
	g_state.cleaning = {18, 19, 21, 1, 5000, 8, MOTOR_12V, false, 0};
	g_state.port = {33, 0};
	g_state.lock = {17, 0};
	init_motor(&g_state.vibrator);
	init_motor(&g_state.cleaning);
	init_servo(&g_state.port);
	init_servo(&g_state.lock);
}


void loop() 
{
	if (Serial.available()) {
        String incoming = Serial.readStringUntil('\n');
		Serial.print("Received: ");
    	Serial.println(incoming);
        if (incoming.length() > 0) {
            handleServoJson(&g_state, incoming.c_str());
            handleMotorJson(&g_state, incoming.c_str());
        }
    }
	handleServo(&g_state);
	handleMotor(&g_state);
}