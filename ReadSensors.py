import paho.mqtt.client as mqtt
import random
import time
import keyboard

sample_time = 100
sampleAnterior = 0
sampleCurrent = 0
delta_sample = 0
band = 0


def time_current_ms():
    return time.time_ns() * 0.000001


def tem():
    return round(random.uniform(0, 130), 2)


def Prs_rct():
    return random.randint(0, 25)


def Prs_clm_rf():
    return random.randint(0, 25)


def Mass():
    return round(random.random(), 2)


publisher = mqtt.Client()
publisher.connect('127.0.0.1', 1883, 60)

while True:
    #x = Mtime_current()
    time.sleep(0.02)
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
            tpm = tem()
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
    if keyboard.is_pressed('q'):
        break
    #y = Mtime_current()
    #print("Tiempo que se demoro en milisegundo todo un ciclo", round(y - x, 2))