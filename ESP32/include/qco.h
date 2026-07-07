#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

typedef enum
{
    MOTOR_5V,
    MOTOR_12V
}       MOTOR_TYPE;

typedef struct
{
    int         pinForward;
    int         pinReverse;
    int         pinEnable;
    int         pwmChannel;
    int         pwmFreq;
    int         pwmResolution;
    MOTOR_TYPE  type;
	bool		forward;
	int			speed;
}       t_motor;

typedef struct
{
    int             pinDir;
    int             pinStep;
    int             minDelayUs;     // delay at 100% speed (fastest)
    int             maxDelayUs;     // delay at 1% speed (slowest)
    bool            forward;
    int             speed;          // 0-100
    unsigned long   lastStepTime;
    bool            stepState;
}       t_stepper;

typedef struct 
{
	int		pin;
	int		angle;
	Servo	servo;
}	t_servo;
typedef struct 
{
	t_motor		vibrator;
	t_stepper	cleaning;
	t_servo 	port;
	t_servo 	lock;
}	state;