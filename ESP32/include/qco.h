#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

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
}       t_motor;

typedef struct 
{
	t_motor	vibrator;
	t_motor	cleaning;
}	state;