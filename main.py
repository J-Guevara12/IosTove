import time
import ntptime
import utime
import ubinascii
from mqtt import MQTTClient
from machine import unique_id,Pin, PWM
import micropython
import network

class Servo:
  """Clase que define a los servos que controlan las perillas de la esufa"""
  def __init__(self, PIN, ID):
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
    #creamos una variable de instancia tipo string que contiene el tópico asignado a ese servo
    self.topic = "uYQgnrskrYUNSUm/cocina/servo{}".format(ID)
  
  
  def nivel(self,pot):
    """metodo que transforma un valor x del 1 al 100 
    en un ciclo de trabajo que equivale al ángulo al 
    que debe ser colocada la perilla de la estufa para 
    dar una llama del x%"""
    angulo = int(float(pot)*(-73/99) + 128.73)
    self.out.duty(angulo)
  
  
  def encender_estufa(self, pot, tiempo):
    """método que enciende la estufa, colocandola primero
    en su llama máxima, encendiendo el chispero y luego 
    llevándola al nivel especificado por pot durante el tiempo 'tiempo' """
    self.nivel(100)
    ch.on()
    time.sleep(1)
    ch.off()
    self.nivel(pot)
    self.dtime = utime.time() + tiempo
  
  def apagar_tiempo(self):
    """método que confirma que si la 'hora' actual es mayor 
    a la 'hora' cuando la estufa debe ser apagada, la apaga"""
    if self.dtime <= utime.time():
      self.out.duty(27)
  
def ajustar_hora():
  """función que sincroniza la hora de nuestro dispositivo con la dada por la nube"""
  ntptime.host = "0.south-america.pool.ntp.org"

  try:
    ntptime.settime()
  except:
    print("Error syncing time")

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
  """pasaría por todos los servos hasta saber cual coincide 
  con el t贸pico, posteriormente decodificaría el código de 
  bytes para devolvernos dos variables con el tiempo de 
  encendido y su nivel, procedería a usar estas variables 
  para encender la estufa"""
  for element in ls:
    if topic.decode() == element.topic:
      ms = msg.decode()
      tm, nv = tratar_mensaje(ms)
      element.encender_estufa(nv,tm)

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
  print('Conectado a %s' % mqtt_server)
  return client

def Reinciar_conexion():
  """función que actua en caso de OSError en la conexión al broker"""
  time.sleep(10)
  machine.reset()

def conectar_wifi():
  """función que se conecta al wifi de nuestro hogar"""
  ssid = 'UNE_HFC_D380' #nombre de la red
  password = 'ACA8F8DF' #contraseña de la red
  wlan = network.WLAN(network.STA_IF)

  wlan.active(True)
  wlan.connect(ssid, password) 

  while wlan.isconnected() == False: #Espera a que se conecte a la red
      pass

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

conectar_wifi()

try:
    client = Conexion_MQTT()
except OSError as e:
    Reinciar_conexion()
#inicia un bucle infinito
while True:
  #comprueba si han llegado mensajes
  disp_pub = client.check_msg()
  #comprueba que todas las estufas están en su estado adecuado
  comprobar_apagado()
  #descansa por 0.1 segundos
  time.sleep(.1)
