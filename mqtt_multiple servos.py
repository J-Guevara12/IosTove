import time
import ubinascii
from mqtt import MQTTClient
from machine import unique_id,Pin, PWM
import micropython
import network

#conectar a Wi-Fi
ssid = 'UNE_HFC_D380' 
password = 'ACA8F8DF' 
wlan = network.WLAN(network.STA_IF)

wlan.active(True)
wlan.connect(ssid, password) 

while wlan.isconnected() == False: #Espera a que se conecte a la red
    pass

print('Conexion con el WiFi %s establecida' % ssid)
print(wlan.ifconfig()) #Muestra la IP y otros datos del Wi-Fi

#definir salidas:

servo1 = PWM(Pin(13))
servo2 = PWM(Pin(12))
servo3 = PWM(Pin(14))
servo4 = PWM(Pin(27))


servo1.freq(50)
servo2.freq(50)
servo3.freq(50)
servo4.freq(50)


servomotores = {
"j44443kp88EsGgX/cocina/servo1" : servo1,
"j44443kp88EsGgX/cocina/servo2" : servo2,
"j44443kp88EsGgX/cocina/servo3" : servo3,
"j44443kp88EsGgX/cocina/servo4" : servo4,
}


def form_sub(topic, msg):
    for topico, actuador in servomotores.items():
      if topic.decode() == topico:
        angulo = int(int(msg.decode())/0.99001)+27
        print(msg.decode(),angulo)
        actuador.duty(angulo)

def Conexion_MQTT():
    client_id = ubinascii.hexlify(unique_id())
    mqtt_server = 'ioticos.org'
    port_mqtt = 1883
    user_mqtt = 'FBK0Ygk5OejxCvY' 
    pswd_mqtt = 'wWUtp5H7udWL5os'
    client = MQTTClient(client_id, mqtt_server,port_mqtt,user_mqtt,pswd_mqtt) 
    client.set_callback(form_sub)
    client.connect()
    for topico in servomotores.keys():
      client.subscribe(topico)
    print('Conectado a %s' % mqtt_server)
    return client

def Reinciar_conexion():
    print('Fallo en la conexion. Intentando de nuevo...')
    time.sleep(10)
    machine.reset()

try:
    client = Conexion_MQTT()
except OSError as e:
    Reinciar_conexion()

while True:
  disp_pub = client.check_msg()
  time.sleep(.1)
