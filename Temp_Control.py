import paho.mqtt.client as mqtt
import time

Tempr = 0
BIT = -1

sample_time = 201 #101 --- 201
sampleAnterior = 0
sampleCurrent = 0
delta_sample = 0
band = 0

topic1 = "planta/reactor/Temp"
topic2 = "server/HMI/bit"

#controlador
kp=0.80
ki=0.85
kd=0.04

def time_current_ms():
    return time.time_ns() * 0.000001


def Cont_PID(SetPoint, temperature, err_int=None, err_an=None):
    print(err_int,err_an)
    err_ac = SetPoint - temperature
    derror = (err_ac - err_an) / 0.201
    err_int = err_int + err_ac * 0.201
    parm_u = kp*err_ac + ki*err_int + kd*derror
    if parm_u >= 100:
        parm_u = 100
    if parm_u < 0:
        parm_u = 0
    if SetPoint == 0:
        parm_u = 0
    err_an = err_ac
    return parm_u


def WhenConnect(client, userdata, flags, rc):
    if rc == 0:
        print("Se ha conectado al servidor")
        subscriber.subscribe([(topic1, 0), (topic2, 0)])
        subscriber.subscribe()
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Error en conexion")


def WhenMessage_tmp(client, userdata, message):
    global Tempr
    Tempr = float(message.payload.decode("utf-8"))
    #print(message.topic + " " + message.payload.decode("utf-8"))


def WhenMessage_bit(client, userdata, message):
    global BIT
    if message.payload.decode("utf-8") == "ON":
        BIT = 1
    if message.payload.decode("utf-8") == "OFF":
        BIT = 0


Connected = False
server_address = "127.0.0.1"
port = 1883

subscriber = mqtt.Client()
subscriber.on_connect = WhenConnect
subscriber.message_callback_add(topic1, WhenMessage_tmp)
subscriber.message_callback_add(topic2, WhenMessage_bit)
subscriber.connect(server_address, port=port)  # connect to broker
subscriber.loop_start() #inicia el hilo que maneja la red y enviar y recibir datos


while Connected != True:  #Wait for connection
    time.sleep(0.01)

try:
    while True:
        if BIT == 1:
            sampleCurrent = time_current_ms()
            delta_sample = sampleCurrent - sampleAnterior
            if delta_sample >= sample_time:
                #print(Tempr)
                data_out = Cont_PID(80,Tempr)
                #print("Aqui control")
                sampleAnterior = sampleCurrent
        if BIT == 0:
            print("Variar manual")

        #print(Tempr)
        """x = time_current_ms()
        print("Hilo principal")
        time.sleep(0.1)
        y = time_current_ms()
        print("Tiempo que se demoro en milisegundo todo un ciclo", round(y - x, 2))"""

except KeyboardInterrupt:
    print("exiting")
    subscriber.disconnect()
    subscriber.loop_stop()
