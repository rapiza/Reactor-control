import paho.mqtt.client as mqtt
import random
import time
#import max6675

sample_time = 100
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
    return random.randint(0, 25)


def Prs_clm_rf():
    return random.randint(0, 25)


def Mass():
    return round(random.random(), 2)


def whenConnect(client, userdata, flags,rc):
    if rc == 0:
        print("Se ha conectado al servidor")
        global Connected
        Connected = True
    else:
        print("Error en conexion")


Connected = False

server_address = "127.0.0.1"
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
        time.sleep(0.01)
        sampleCurrent = time_current_ms()
        delta_sample = sampleCurrent - sampleAnterior
        if delta_sample >= sample_time:
            pres1 = Prs_rct()
            pres2 = Prs_clm_rf()
            mass = Mass()
            if band == 0:
                datos = f"{pres1};{pres2};{mass}\n"
                print(datos)
                publisher.publish("planta/reactor/Pres1", pres1)
                publisher.publish("planta/reflujo/Pres2", pres2)
                publisher.publish("planta/reactor/Mass", mass)
            if band == 1:
                tpm = tem() #max6675.read_temp(cs)
                datos = f"{pres1};{pres2};{mass};T{tpm}K\n"
                print(datos)
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
