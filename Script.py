#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 03:22:24 2020

@author: nishu
"""

import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import time
#import numpy as np 
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation
import adafruit_mcp4725

import RPi.GPIO as GPIO

#import pandas as pd
from datetime import datetime

#%%

from All_F import ads, assign_add
from All_F import discharge, charge 
from All_F import cycle_discharge_first, cycle_charge_first

#%%
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) #MOSFET relay + charge/Discharge relay

GPIO.setup(22,GPIO.OUT) #Battery relay
#GPIO.setup(23,GPIO.OUT) #Red LED
GPIO.setup(24,GPIO.OUT) #Blue LED



GPIO.output(17,GPIO.LOW)

GPIO.output(22,GPIO.LOW) 
#GPIO.output(23,GPIO.LOW)
GPIO.output(24,GPIO.LOW)
#%%


ads(G=1)

#%%
e1=0
assign_add()

#%%
####Example scripts

#discharge(name='1000uF',I_D=1e-5,R=9740,vbmax=4.0,vbmin=0,TD=600,TL_D=True,interval=10)
#charge(name='1000uF',I_C=1e-5,R=9850,vbmax=0.2,vbmin=0,TC=600,TL_C=True,interval=10)
#cycle_charge_first(name='1000uF',I_C=1e-5,I_D=1e-5,R=9870,vbmax=3.8,vbmin=0,TD=30,TC=30,cycles=500,TL_C=True,TL_D=True,interval=30)
