import paho.mqtt.client as mqtt #doc https://pypi.org/project/paho-mqtt/#single
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
#import max6675

#weight config
GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
hx = HX711(dout_pin=5, pd_sck_pin=6) # create objet of hx711 class
hx.set_offset(24750) #offset on 0
hx.set_scale_ratio(21250/160) #scale ratio to convert in gr

#adc config
i2c = busio.I2C(board.SCL, board.SDA) # Create the I2C bus
ads = ADS.ADS1115(i2c) # Create the ADC object using the I2C bus
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P0, ADS.P1)

#sample time setting
sample_time = 1000
sampleAnterior = 0
sampleCurrent = 0
delta_sample = 0
band = 0


def time_current_ms():
    return time.time_ns() * 0.000001


# set the pin for communicate with MAX6675
cs = 22
sck = 18
so = 16
#max6675.set_pin(CS, SCK, SO, unit)   [unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
#max6675.set_pin(cs, sck, so, 1)
def tem():
    return round(random.uniform(0, 130), 2)

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
            if band == 0:
                datos = f"{pres1};{pres2};{mass}\n"
                #print(datos)
                publisher.publish("planta/reactor/Pres1", pres1)
                publisher.publish("planta/reflujo/Pres2", pres2)
                publisher.publish("planta/reactor/Mass", mass)
            if band == 1:
                tpm = tem() #max6675.read_temp(cs)
                datos = f"{pres1};{pres2};{mass};T{tpm}K\n"
                #print(datos)
                publisher.publish("planta/reactor/Pres1", pres1)
                publisher.publish("planta/reflujo/Pres2", pres2)
                publisher.publish("planta/reactor/Mass", mass)
                publisher.publish("planta/reactor/Temp", tpm)
            band += 1
            if band == 2:
                band = 0
            sampleAnterior = sampleCurrent
        #y = time_current_ms()
        #print("Tiempo que se demoro en milisegundo todo un ciclo", round(y - x, 2))

except KeyboardInterrupt:
    publisher.disconnect()
    publisher.loop_stop()
finally:
    GPIO.cleanup()
