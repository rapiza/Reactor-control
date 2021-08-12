import paho.mqtt.client as mqtt
import random
import time
#weight libs
import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711
#adc libs
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
#max6675 lib
from max6675 import MAX6675, MAX6675Error



#weight config
#GPIO.setmode(GPIO.BOARD) # set GPIO pin mode to BOARD
hx = HX711(dout_pin=5, pd_sck_pin=6) # create objet of hx711 class
hx.set_offset(24750) #offset on 0
hx.set_scale_ratio(21250/160) #scale ratio to convert in gr

#adc config
i2c = busio.I2C(board.SCL, board.SDA) # Create the I2C bus
ads = ADS.ADS1115(i2c) # Create the ADC object using the I2C bus
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P0, ADS.P1)

#max config
cs_pin1 =  22#15 
clock_pin1 = 17#11
data_pin1 = 27#13

cs_pin2 =  8#24
clock_pin2 = 11#23
data_pin2 = 9#21
units = "c"

#sample time setting
sample_time = 1000
sampleAnterior = 0
sampleCurrent = 0
delta_sample = 0
band = 0


def time_current_ms():
    return time.time_ns() * 0.000001


def Temp_rct():
    
    thermocouple_rct = MAX6675(cs_pin1, clock_pin1, data_pin1, units)
    temp_rct=thermocouple_rct.get()
    print(temp_rct,'°C TMP_RCT\n')
    
def Temp_tlv():
    thermocouple_tlv = MAX6675(cs_pin2, clock_pin2, data_pin2, units)
    temp_tlv=thermocouple_tlv.get()
    print(temp_tlv, '°C TMP_TLV\n')

def Prs_rct():
    prs_rct=26.0684*chan0.voltage+14.6959
    print(prs_rct, 'PSI\n')
    return (prs_rct)


def Prs_clm_rf():
    prs_clm_rf= 26.0684*chan1.voltage+14.6959
    print(prs_clm_rf, 'PSI\n')
    return (prs_clm_rf)


def Mass():
    peso=1.0*hx.get_weight_mean(1)
    print(peso, 'gr\n')
    return (peso)


def whenConnect(client, userdata, flags,rc):
    if rc == 0:
        print("Se ha conectado al servidor")
        global Connected
        Connected = True
    else:
        print("Error en conexion")


Connected = False

server_address = "192.168.0.101"
port = 1883

publisher = mqtt.Client()
publisher.on_connect = whenConnect
publisher.connect(server_address,port,60)
publisher.loop_start()

while Connected != True: #Esperar para que exista conexion
    time.sleep(0.01)

try:
    while True:
        #x = time_current_ms()
        time.sleep(0.001)
        sampleCurrent = time_current_ms()
        delta_sample = sampleCurrent - sampleAnterior
        
        if delta_sample >= sample_time:
            
            pres1 = Prs_rct()
            pres2 = Prs_clm_rf()
            mass = Mass()
            temp_rct= Temp_rct()
            temp_tlv= Temp_tlv() 
            #print(datos)
            publisher.publish("planta/reactor/Pres1", pres1)
            publisher.publish("planta/reflujo/Pres2", pres2)
            publisher.publish("planta/reactor/Mass", mass)
            publisher.publish("planta/reactor/Temp", temp_rct)
            publisher.publish("planta/tolva/Temp2", temp_tlv)
            
            sampleAnterior = sampleCurrent
        #y = time_current_ms()
        #print("Tiempo que se demoro en milisegundo todo un ciclo", round(y - x, 2))

except KeyboardInterrupt:
    publisher.disconnect()
    publisher.loop_stop()
finally:
    GPIO.cleanup()
