#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 11:18:10 2020

@author: nishu
"""
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import time

import adafruit_mcp4725

import RPi.GPIO as GPIO

from datetime import datetime
import sys
#%%


def ads(G):
    global VS, VB
    ads = ADS.ADS1115(i2c)
    ads.gain=G
    VB=AnalogIn(ads, ADS.P0, ADS.P1)
    VS=AnalogIn(ads, ADS.P2, ADS.P3)
    
#%%

e1=0
def assign_add():
    global dac, e1
   
    try:
        add=i2c.scan()
        if add[1]==96:
            dac = adafruit_mcp4725.MCP4725(i2c,address=0x60)
        
        if add[1]==97:
            dac = adafruit_mcp4725.MCP4725(i2c,address=0x61)
    except IndexError: 
            e1=e1+1
            assign_add() 
            if e1>100:
                GPIO.output(17,GPIO.LOW)
                GPIO.output(22,GPIO.LOW) 
                GPIO.output(24,GPIO.LOW)
                                
                raise IndexError
                
    except ValueError: 
            e1=e1+1
            assign_add() 
            if e1>100:
                GPIO.output(17,GPIO.LOW)
                GPIO.output(22,GPIO.LOW) 
                GPIO.output(24,GPIO.LOW)
                                
                raise IndexError
                
#%%

def ocp(name,T,interval):
    global VB,dac
    now = datetime.now()
    NAME=name+'_OCP'+str(now.strftime("%d-%m-%Y-%H:%M:%S"))
    T0=time.time()
    o=0
    while True:
        try:
            T1=time.time()-T0
            vb=VB.voltage
            if o%interval==0:
                with open(NAME+'livedata'+'.csv',mode="a")as file:
                    file.write(f"{T1},{vb}\n") 
            sys.stdout.write('\r'+'Battery Voltage: '+str(round(vb,4))+'Time (s):'+str(round(T1,2)))
            sys.stdout.flush()
            o=o+1
            if T1 >T:
                break
        except KeyboardInterrupt:
            sys.exit()
        
        
#%%
def discharge(name,I_D,R,vbmax,vbmin,TD,TL_D=True,interval=10):
    global VB, VS, dac, ESC
    ESC=False
    now = datetime.now()
    NAME=name+'_Discharge_'+str(I_D)+'A_'+str(now.strftime("%d-%m-%Y-%H:%M:%S"))
    with open(NAME+'.csv',mode="a")as file:
       file.write('t,V,I\n') 
    
    # times=[]
    # Vb=[]
    # I=[]
   
    e=0
    d=0
  
    
        
    
    vmos=I_D*R*1000
    GPIO.output(17,GPIO.LOW)
    GPIO.output(24,GPIO.HIGH)
    GPIO.output(22,GPIO.HIGH)
    time.sleep(0.1)
    
    T0D=time.time()
######################DISCHARGE####################        
    while True:
        try: 
            B=int(round((vmos/5000)*4095))
            if B > 4094:
                print('Error! DAC saturated (High)')
                break
            if B < 0:
                print('Error! DAC saturated (Low)')
                break
            dac.raw_value = B
            
            vb=VB.voltage
            i=VS.voltage/R
            T1=time.time()-T0D
            if d % interval ==0: 
                # times.append(T1) 
                # Vb.append(vb)
                # I.append(-1*i)
                with open(NAME+'.csv',mode="a")as file:
                    file.write(f"{T1},{vb},{-1*i}\n")
                    
            
            iError=i-I_D
            if abs(iError) > 0.05*I_D:
                vmos=vmos-(iError*R*1000)
            
            TDD=time.time()-T0D
            if d >2:
                if vb > vbmax:
                    print('Battery voltage high')
                    break
                if vb < vbmin: 
                    print('Battery voltage low')
                    break
                
                if TL_D: 
                    if TDD > TD:
                        break
            
                
            d=d+1
            print("Mode= Discharge Battery Voltage: "+str(round(vb,4))+" DAC: "+str(B)+' Current: '+str(round(i,4))+" Time (s):"+str(round(TDD,2))+" Errors: "+str(e),end='\r')
           

            
        except OSError:
            
            e=e+1
            assign_add()
            if e >100: 
                print('Too many OSErrors')
                ESC=True
                break
            else: 
                continue
        except ValueError:
            e=e+1 
            assign_add()
            if e >100: 
                print('Too many ValueErrors')
                ESC=True
                break
            else: continue
        
        except IndexError: 
            e=e+1
            assign_add()
            if e >100: 
                print('Too many ValueErrors')
                ESC=True
                break
            else: continue
        
        except KeyboardInterrupt:
            
            GPIO.output(22,GPIO.LOW)
            dac.raw_value=0
            GPIO.output(24,GPIO.LOW)
            ESC=True
        
            break      
           
     
    if ESC:
        sys.exit()
    
    GPIO.output(22,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    GPIO.output(24,GPIO.LOW)
    
#%%


def charge(name,I_C,R,vbmax,vbmin,TC,TL_C=True,interval=10):
    global VB, VS, dac,ESC
    ESC=False
    now = datetime.now()
    NAME=name+'_Charge_'+str(I_C)+'A_'+str(now.strftime("%d-%m-%Y-%H:%M:%S"))
    with open(NAME+'.csv',mode="a")as file:
       file.write('t,V,I\n')
   
    e=0
    c=0

    vmos=I_C*R*1000

    GPIO.output(17,GPIO.HIGH)
    GPIO.output(22,GPIO.HIGH)
    
    time.sleep(0.1)
    
#########CHARGE#####################
    T0C=time.time()
    
    while True: 
        try: 
            B=int(round((vmos/5000)*4095))
            if B > 4094:
                print('Error! DAC saturated (High)')
                break
            if B < 0:
                print('Error! DAC saturated (Low)')
                break
            dac.raw_value = B
            vb=VB.voltage
            i=VS.voltage/R
            T1=time.time()-T0C
            if c % interval ==0: 

                with open(NAME+'.csv',mode="a")as file:
                    file.write(f"{T1},{vb},{i}\n")
            iError=i-I_C

            if abs(iError) > 0.05*I_C:
                vmos=vmos-(iError*R*1000)
         
            TCC=time.time()-T0C
            if c>2:
                if vb > vbmax:
                    print('Battery voltage high')
                    break
                if vb < vbmin: 
                    print('Battery voltage low')
                    break
            
                if TL_C:
                    if TCC > TC:
                        break
            c=c+1
            print('Mode= Charge Battery Voltage: '+str(round(vb,4))+' DAC: '+str(B)+' Current: '+str(round(i,6))+'Time (s):'+str(round(TCC,2))+' Errors: '+str(e),end='\r')
            
            
        except OSError:
            e=e+1
            assign_add()
            if e >100: 
                print('Too many OSErrors')
                ESC=True
                break
            else: 
                continue
        except ValueError:
            e=e+1 
            assign_add()
            if e >100: 
                print('Too many ValueErrors')
                ESC=True
                break
            else: continue
        
        except IndexError: 
            e=e+1
            assign_add()
            if e >100: 
                print('Too many ValueErrors')
                ESC=True
                break
            else: continue
        
        except KeyboardInterrupt:
            ESC=True
            GPIO.output(22,GPIO.LOW)
            GPIO.output(17,GPIO.LOW)
            dac.raw_value=0
            GPIO.output(24,GPIO.LOW)
            ESC=True
            break 
            
    if ESC:
        sys.exit()
    
    GPIO.output(22,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    
#%%
def cycle_discharge_first(name,I_C,I_D,R,vbmax,vbmin,TD,TC,cycles,TL_C=True,TL_D=True,interval=10):
    global VB, VS, dac
    
    now = datetime.now()
    NAME=name+str(cycles)+'Cycles'+'_D'+str(I_D)+'A_C'+str(I_C)+'A_'+str(now.strftime("%d-%m-%Y-%H:%M:%S"))
    with open(NAME+'livedata'+'.csv',mode="a")as file:
       file.write('t,V,I\n') 
    ESC=False

    t0=time.time()
    e=0
  
    for j in range(cycles):
        c=0
        d=0 
        vmos=I_D*R*1000
        GPIO.output(17,GPIO.LOW)
        GPIO.output(24,GPIO.HIGH)
        GPIO.output(22,GPIO.HIGH)
        time.sleep(0.1)
        
        T0D=time.time()
######################DISCHARGE####################        
        while True:
            try: 
                B=int(round((vmos/5000)*4095))
                if B > 4094:
                    print('Error! DAC saturated (High)')
                    break
                if B < 0:
                    print('Error! DAC saturated (Low)')
                    break
                dac.raw_value = B
                
                vb=VB.voltage
                i=VS.voltage/R
                T1=time.time()-t0
                if d % interval ==0: 

                    with open(NAME+'.csv',mode="a")as file:
                        file.write(f"{T1},{vb},{-1*i}\n")
                        
                
                iError=i-I_D
                if abs(iError) > 0.05*I_D:
                    vmos=vmos-(iError*R*1000)
                
                TDD=time.time()-T0D
                if d >10:
                    if vb > vbmax:
                        print('Battery voltage high')
                        break
                    if vb < vbmin: 
                        print('Battery voltage low')
                        break
                    
                    if TL_D: 
                        if TDD > TD:
                            break
                
                    
                d=d+1
                print('Mode= Discharge Cycle: '+str(j)+' Battery Voltage: '+str(round(vb,4))+' DAC: '+str(B)+' Current: '+str(round(i,4))+' Time (s):'+str(round(TDD,2))+' Errors: '+str(e),end='\r')
                
                
            except OSError:
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many OSErrors')
                    ESC=True
                    break
                else: 
                    continue
            except ValueError:
                e=e+1 
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    ESC=True
                    break
                else: continue
            
            except IndexError: 
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    ESC=True
                    break
                else: continue
            
            except KeyboardInterrupt:
                ESC=True
                GPIO.output(22,GPIO.LOW)
                dac.raw_value=0
                GPIO.output(24,GPIO.LOW)
                break      
         
        if ESC:
            break
        
    
        GPIO.output(24,GPIO.LOW)
        GPIO.output(22,GPIO.LOW)
        
        vmos=I_C*R*1000
        e=0
        GPIO.output(17,GPIO.HIGH)
        GPIO.output(22,GPIO.HIGH)
        time.sleep(0.1)
        
        T0C=time.time()
########################CHARGE#################        
        while True: 
            
            try: 
                B=int(round((vmos/5000)*4095))
                if B > 4094:
                    print('Error! DAC saturated (High)')
                    break
                if B < 0:
                    print('Error! DAC saturated (Low)')
                    break
                dac.raw_value = B
                vb=VB.voltage
                i=VS.voltage/R
                T1=time.time()-t0
                if c % interval ==0: 

                    with open(NAME+'.csv',mode="a")as file:
                        file.write(f"{T1},{vb},{i}\n")
                iError=i-I_C
                if abs(iError) > 0.05*I_C:
                    vmos=vmos-(iError*R*1000)
                
                TCC= time.time()-T0C
                if c>10:
                    if vb > vbmax:
                        print('Battery voltage high')
                        break
                    if vb < vbmin: 
                        print('Battery voltage low')
                        break
                    
                    if TL_C: 
                        if  TCC> TC:
                            break
                c=c+1
                print('Mode= Charge Cycle: '+str(j)+ ' Battery Voltage: '+str(round(vb,4))+' DAC: '+str(B)+' Current: '+str(round(i,4))+'Time (s):'+str(round(TCC,2))+' Errors: '+str(e),end='\r')
                
            except OSError:
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many OSErrors')
                    ESC=True
                    break
                else: 
                    continue
            except ValueError:
                e=e+1 
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    ESC=True
                    break
                else: continue
            
            except IndexError: 
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    ESC=True
                    break
                else: continue
            
            except KeyboardInterrupt:
                ESC=True
                GPIO.output(22,GPIO.LOW)
                GPIO.output(17,GPIO.HIGH)
                dac.raw_value=0
                break 
            
        GPIO.output(22,GPIO.LOW)
        GPIO.output(17,GPIO.LOW)


        if ESC:
            break
        
    
    dac.raw_value=0
    GPIO.output(22,GPIO.LOW)
    GPIO.output(24,GPIO.LOW)
    
    if ESC:
        sys.exit()  
            
            
#%%

def cycle_charge_first(name,I_C,I_D,R,vbmax,vbmin,TD,TC,cycles,TL_C=True,TL_D=True,interval=10):
    global VB, VS, dac
    now = datetime.now()
    NAME=name+str(cycles)+'Cycles'+'_D'+str(I_D)+'A_C'+str(I_C)+'A_'+str(now.strftime("%d-%m-%Y-%H:%M:%S"))
    with open(NAME+'livedata'+'.csv',mode="a")as file:
       file.write('t,V,I\n')
    ESC=False

    t0=time.time()
    
    e=0
    GPIO.output(22,GPIO.HIGH)


    for j in range(cycles):
        c=0
        d=0
        vmos=I_C*R*1000

        GPIO.output(17,GPIO.HIGH)
        
        time.sleep(0.1)
        
    #########CHARGE#####################
        T0C=time.time()
        
        while True: 
            try: 
                B=int(round((vmos/5000)*4095))
                if B > 4094:
                    print('Error! DAC saturated (High)')
                    break
                if B < 0:
                    print('Error! DAC saturated (Low)')
                    break
                dac.raw_value = B
                vb=VB.voltage
                i=VS.voltage/R
                T1=time.time()-t0
                if c % interval ==0: 

                    with open(NAME+'.csv',mode="a")as file:
                        file.write(f"{T1},{vb},{i}\n")
                iError=i-I_C

                if abs(iError) > 0.05*I_C:
                    vmos=vmos-(iError*R*1000)
                
                TCC=time.time()-T0C
                if c>2:
                    if vb > vbmax:
                        print('Battery voltage high')
                        break
                    if vb < vbmin: 
                        print('Battery voltage low')
                        break
                
                    if TL_C:
                        if TCC > TC:
                            break
                c=c+1
                print('Mode= Charge Cycle: '+str(j)+' Battery Voltage: '+str(round(vb,4))+' DAC: '+str(B)+' Current: '+str(round(i,6))+'Time (s):'+str(round(TCC,2))+' Errors: '+str(e),end='\r')
                
            except OSError:
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many OSErrors')
                    ESC=True
                    break
                else: 
                    continue
            except ValueError:
                e=e+1 
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    ESC=True
                    break
                else: continue
            
            except IndexError: 
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    ESC=True
                    break
                else: continue
            
            except KeyboardInterrupt:
                ESC=True
                GPIO.output(22,GPIO.LOW)
                GPIO.output(17,GPIO.LOW)
                dac.raw_value=0
                GPIO.output(24,GPIO.LOW)
                break 
            
        GPIO.output(17,GPIO.LOW)

        if ESC:
            break
        
        
        vmos=I_D*R*1000
        B=int(round((vmos/5000)*4095))
        dac.raw_value = B
       
        GPIO.output(24,GPIO.HIGH)
        time.sleep(0.1)
        
        T0D=time.time()
        
###########DISCHARGE#############
        while True:
            try: 
                B=int(round((vmos/5000)*4095))
                if B > 4094:
                    print('Error! DAC saturated (High)')
                    break
                if B < 0:
                    print('Error! DAC saturated (Low)')
                    break
                dac.raw_value = B
                
                vb=VB.voltage
                i=VS.voltage/R
                T1=time.time()-t0
                if d % interval ==0: 

                    with open(NAME+'.csv',mode="a")as file:
                        file.write(f"{T1},{vb},{-1*i}\n")
                
                iError=i-I_D
                if abs(iError) > 0.05*I_D:
                    vmos=vmos-(iError*R*1000)
                    
                TDD=time.time() -T0D
                if d >2:
                    if vb > vbmax:
                        print('Battery voltage high')
                        break
                    if vb < vbmin: 
                        print('Battery voltage low')
                        break
                
                    if TL_D:
                        if TDD> TD:
                            break
                
                    
                d=d+1
                print('Mode= Discharge Cycle: '+str(j)+' Battery Voltage: '+str(round(vb,4))+' DAC: '+str(B)+' Current: '+str(round(i,6))+' Time (s):'+str(round(TDD,2))+' Errors: '+str(e),end='\r')
                
                
            except OSError:
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many OSErrors')
                    break
                else: 
                    continue
            except ValueError:
                e=e+1 
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    break
                else: continue
            
            except IndexError: 
                e=e+1
                assign_add()
                if e >100: 
                    print('Too many ValueErrors')
                    ESC=True
                    break
                else: continue
            
            except KeyboardInterrupt:
                ESC=True
                GPIO.output(22,GPIO.LOW)
                dac.raw_value=0
                GPIO.output(24,GPIO.LOW)
                break   
            
        GPIO.output(17,GPIO.LOW)
         
        vmos=I_C*R*1000
        B=int(round((vmos/5000)*4095))
        dac.raw_value = B
       
        
        GPIO.output(24,GPIO.LOW)
        
        if ESC:
            break
        
    
    GPIO.output(22,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    dac.raw_value=0
    GPIO.output(24,GPIO.LOW)

    if ESC:
        sys.exit()

#%%
