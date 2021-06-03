#importar librerías:

import time
import ntptime
import utime
import ubinascii
from mqtt import MQTTClient
from machine import unique_id,Pin, PWM, I2C, TouchPad, reset
import ssd1306
import micropython
import network

class Servo:
  """Clase que define a los servos que controlan las perillas de la esufa"""
  def __init__(self,PIN,ID):
    """
    Construcción de la instancia:
    
    PIN : asigna un pin de el microcontrolador a esta salida:
    
    ID : asigna una ID que NO se puede repetir para propósitos 
    del protocolo de comunicación
    """

    #asignamos el pin como salida de modulación por ancho de pulso a una frecuencia de 50 Hz
    self.out = PWM(Pin(PIN))
    self.out.freq(50)
    #colocamos ciclo de trabajo como 27, que pone al servo en un ángulo que cierra el paso de gas
    self.out.duty(27)
    #dtime : momento en el que la estufa va a ser apagada
    self.dtime = 0
    #creamos una variable de instancia tipo string que 
    # contiene el tópico asignado a ese servo
    self.topic = "uYQgnrskrYUNSUm/cocina/servo{}".format(ID)
    self.ID = ID
  
  
  def nivel(self,pot):
    """método que transforma un valor x del 1 al 100 
    en un ciclo de trabajo que equivale al ángulo al 
    que debe ser colocada la perilla de la estufa para 
    dar una llama del x%"""
    angulo = int(float(pot)*(-73/99) + 128.73)
    x = 1 if angulo > self.out.duty() else -1
    times = 1/abs(angulo-self.out.duty())
    for i in range(self.out.duty(),angulo,x):
      self.out.duty(i)
      time.sleep(times)
    self.out.duty(angulo)
  
  
  def encender_estufa(self,pot,tiempo):
    """método que enciende la estufa, colocandola primero
    en su llama máxima, encendiendo el chispero y luego 
    llevándola al nivel especificado por 'pot' durante el tiempo 'tiempo' """
    self.nivel(100)
    ch.on()
    time.sleep(.1)
    ch.off()
    self.nivel(pot)
    self.dtime = utime.time() + tiempo
  
  def apagar_tiempo(self):
    """método que confirma que si la 'hora' actual es mayor 
    a la 'hora' cuando la estufa debe ser apagada, la apaga"""
    if self.dtime <= utime.time():
      self.out.duty(27)

def comprobar_apagado():
  """función que comprueba que todas nuestras
  estufas están apagadas si el tiempo ya pasó"""
  for element in ls:
    element.apagar_tiempo()

def tratar_mensaje(msg):
  """una vez llegue el mensaje de MQTT, lo transformamos en una 
  variable de tiempo en segundos que indica el tiempo que va a estar
  encendida nuestra estufa y el nivel"""
  x,y,z,w = tuple(msg.replace(",",":").split(":"))
  tm = (int(x)*3600+int(y)*60+int(z))
  return tm,int(w)
  
def form_sub(topic, msg):
  """pasará por todos los servos hasta saber cual coincide 
  con el tópico, posteriormente decodificará el código de 
  bytes para devolvernos dos variables con el tiempo de 
  encendido y su nivel, procederá a usar estas variables 
  para encender la estufa"""
  for element in ls:
    if topic.decode() == element.topic:
      ms = msg.decode()
      tm, nv = tratar_mensaje(ms)
      element.encender_estufa(nv,tm)

def notificar():
  """dado el caso de que el valor del módulo MQ-4 sea 0 
  (hay un exceso de gas), cerrará todos los servos y enviará
  un mensaje de alarma a todos nuestros dispositivos subscitos 
  a el tópico alarma, la variable lock sirve para que solo se 
  envíe la alarma una vez"""
  global lock
  if  gas.value() == 0 and not lock:
    client.publish("uYQgnrskrYUNSUm/alarma","fuga de gas")
    lock = True
    for element in ls:
      element.out.duty(27)
    printOLED("FUGA DE GAS")

def printOLED(string,x=0,y=5):
  """función que imprime en una linea el texto especificado"""
  oled.fill(0)
  oled.text(string,0,0)
  oled.show()

def printOLEDh(ID,string,x=0,y=5):
  """imprime en el oled la forma

  estufa 'ID':
  Hora:minutos:segundos

  Con un parpadeo en los : entre los tiempos
  """
  oled.fill(0)
  oled.text("Estufa "+ str(ID)+":",x,y)
  oled.text(string,x,y+15)
  oled.show()

def printH(dx):
  """asignado un indice 'dx' que va de 0 a 3, nos presenta en la pantalla
   con la ayuda de la  funciónprintOLEDh el tiempo que falta para que la estufa 
   especificada por 'dx' se apague, dado el caso que la estufa esté apagada muestra el mensaje:

   estufa dx:
   esperando..."""
  crr = ls[dx]
  tm = crr.dtime - utime.time()
  if tm > 0:
    h = tm//3600
    m = (tm%3600)//60
    s = tm%60
    tf = "{}: {}: {}".format(h,m,s) if s%2 == 0 else "{}  {}  {}".format(h,m,s)
    
    printOLEDh(dx+1,tf,y = 10)
  else:
    if utime.time()%3 == 0:
      printOLEDh(dx+1,"Esperando.",y = 10)
    if utime.time()%3 == 1:
      printOLEDh(dx+1,"Esperando..", y = 10)
    if utime.time()%3 == 2:
      printOLEDh(dx+1,"Esperando...", y = 10)


def changestate():
  """funcion qu cuando percibe una baja en el sensor 
  táctil capacitivo (está siendo tocado), comprueba que cuando se suelte 
  el sensor, a la variable index que va de 0 a 3, se le sume 1"""
  global index
  if t.read() < 400:
      time.sleep(.1)
      if t.read() > 400:
          index = (index +1)%4


def Conexion_MQTT():
  """se conecta al broker MQTT"""
  client_id = ubinascii.hexlify(unique_id())
  mqtt_server = 'ioticos.org'
  port_mqtt = 1883
  user_mqtt = 'ioLpAcWZvzlT0za' 
  pswd_mqtt = 'WW5JtB08sUnXvFr'
  client = MQTTClient(client_id, mqtt_server,port_mqtt,user_mqtt,pswd_mqtt) 
  client.set_callback(form_sub)
  client.connect()
  for element in ls:
    client.subscribe(element.topic)
  client.subscribe("uYQgnrskrYUNSUm/alarma")
  printOLED('Conectado a MQTT')
  return client

def Reinciar_conexion():
  """función que actua en caso de OSError en la conexión"""
  time.sleep(10)
  reset()

  
def conectar_wifi():
  """función que se conecta al wifi de nuestro hogar"""
  ssid = 'UNE_HFC_D380' #nombre de la red
  password = 'ACA8F8DF' #contrase帽a de la red
  wlan = network.WLAN(network.STA_IF)

  wlan.active(True)
  wlan.connect(ssid, password) 

  while wlan.isconnected() == False: #Espera a que se conecte a la red
    pass
printOLED("Conexion exitosa!!")


#definimos las variables correspondientes a los servos con sus pines y IDs
s1 = Servo(13,1)
s2 = Servo(12,2)
s3 = Servo(14,3)
s4 = Servo(27,4)

#agrupamos todos los servos en una sola lista para facilitar el trabajo
ls = [s1,s2,s3,s4]

#definimos el chispero
ch = Pin(26,Pin.OUT)
ch.off()

#inicia el sensor táctil capacitivo
t = TouchPad(Pin(32))

#inicia la entrada de la alerta de gas como digital, estado 1 significa que hay gas, esado 2 ue no hay
gas = Pin(35,Pin.IN,Pin.PULL_UP)

#inicia los pines que van a ser usados por la comunicación I2C, 
#posteriormente inicia la variable oled para usar las funciones de la librería ssd1306
i2c = I2C(-1, scl=Pin(25), sda=Pin(33))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

#se conecta al WiFi, dado el caso de un error se reinicia el microcontrolador
try:
    client = conectar_wifi()
except OSError:
    Reinciar_conexion()

#se conecta al broker MQTT, dado el caso de un error se reinicia el microcontrolador
try:
    client = Conexion_MQTT()
except OSError as e:
    Reinciar_conexion()

#indice con la estufa que se va a mostrar en la pantalla OLED
index = 0
#inicia el ock como falso para permitir que se pueda activa la aarma por fuga de gas
lock = False

#inicia un bucle infinito
while True:
  #comprueba si han llegado mensajes
  disp_pub = client.check_msg()
  #comprueba que todas las estufas están en su estado adecuado
  comprobar_apagado()
  #cambia el estado de index dado el caso de que el sensor capacitivo sea tocado
  changestate()
  #imprime el tiempo restante del encendido de la estufa indicada por index
  printH(index)
  #comprueba que si hay fuga de gas, cierre las válvulas y mande una notificación
  notificar()
  #descansa por 0.01 segundos
  time.sleep(.01)
