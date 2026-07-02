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

    int maxPWM = 255;

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