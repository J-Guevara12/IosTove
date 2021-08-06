# IosTove:

_La idea de Iostove es la automatización de las cocinas de gas bajo el concepto del IoT, es decir que esta reciba y envíe información que sirva tanto para automatización como análisis._

## Prerrequitos

_En orden de poder ejecutar el programa, y que este funcione para automatizar tu cocina, se necesita como mínimo:_
- Acceso estable a internet
- Un broker MQTT
- Python 3
- 4 servomotores
- 1 esp32 Wroom-32
- 1 módulo MQ-4
- 1 pantalla OLED
- 1 válvula solenoide


## Instalación 🔧

_Lo primero será descargar los archivos contenidos en la carpeta code de este repositorio, posteriormente entrar al archivo **main.py**, hacer las siguientes modificaciones:_

```
167  mqtt_server = ''   #colocar la dirección de nustro broker MQTT
168  port_mqtt =        #colocar el puerto de el broker
169  user_mqtt = ''     #colocar el usuario del broker
170  pswd_mqtt = ''     #colocar la contraseña
```
```
188 ssid = ''       #colocar nombre de la red
189 password = ''   #colocar contraseña de la red
```

_Debemos flashear microPython en nuestra es-32, para eso podemos guiarnos por [la guía de inicio de micropython](https://docs.micropython.org/en/v1.15/esp8266/tutorial/pins.html "Getting started with MicroPython on the ESP32")_

_También debemos instalar __ampy__ que es una librería de Adafruit que servirá para cargar el código en nuestro microcontrolador, esto lo haremos mediante el comando:_
```
pip install adafruit-ampy
```

_se debe conectar el esp-32 a una pc via USB, haciendo uso de la conexión UART, (sea mediante un burner o una placa de desarrollo), una vez hecho esto navegaremos hasta la carpeta dónde están nuestros archivos .py mediante el terminal y ejecutaremos individualmente las siguientes lineas:_


```
ampy --port COM5 put main.py
```
```
ampy --port COM5 put mqtt.py
```
```
ampy --port COM5 put ssd1306.py
```


podría ser necesario cambiar COM5 por el puerto en el que esté conectado nuestro dispositivo.


### Montaje ⌨️

_Una vez listo el esp32, debemos hacer el montaje, en este caso debemos conectar toda la alimentación de los servomotores en paralelo a una fuente de 5V, y hacer las siguientes conexiones:_
- IO13 al primer servo.
- IO12 al segundo servo.
- IO14 al tercer servo.
- IO27 al cuarto servo.
- VIN a el positivo de la fuente de 5V.
- GND a la tierra de la fuente.
- 3V3 a vcc de la pantalla OLED.
- GND de la pantalla OLED a tierra.
- IO25 a SCL de la pantalla OLED.
- IO33 a SDA de la pantalla OLED.
- IO26 al encendido del chispero (puede requerir de un circuito de protección o amplificación).
- IO32 se conecta aun cable abierto o a una placa de material conductor, pues es el táctil.
- IO35 a el DO del módulo MQ-4.
- Alimentar con 5V el módulo MQ-4.

_Si se está usando la [PCB](https://oshwlab.com/Juan_Guevara/iostove "Página del pryecto de la PCB") personalizada para el proyecto, simplemente debemos conectar un cargador microUSB (pereferiblemente de cable corto) y con cables hacer las conexiones que se especifican en la capa serigráfica._

_finalmente al conectarse a la alimentación la pantalla deberá encender, mostrar primero __conexion exitosa__, luego __conectado a MQTT__ y finalmente decir __estufa 1, esperando...__, a partir de ese momento, usando un cliente de MQTT podremos enviar un mensaje de la forma:_

  ```Horas:minutos:segundos,nivel```
dónde las 3 primeras variables serán el tiempo que la estufa encenderá, y la cuarta indica el nivel de la llama, ejemplo ```2:30:12,80```.

Si se toca el sensor táctil pasaremos de la estufa 1 a la 2 y así sucesivamente.

## video de demostración 📌

[![IMAGE ALT TEXT](http://img.youtube.com/vi/OUU-_lDAZyY/0.jpg)](http://www.youtube.com/watch?v=OUU-_lDAZyY "Automatización cocina")

## Problemas encontrados en el proceso
- Falta de la libería datetime y todas las funciones de la librería time.
- Mala o nula documentación en alguno de los procesos.
- Falta de una fuente de alimentación.
- El cargador que se usó para alimentar todo el circuito era muy largo y solía causar caídas de tensión al momento de ejecutar dos o más servos, la solución fue usar una fuente auxiliar
- Falta de multímetro.
- Dificultades en encontrar un broker MQTT gratuito.
- Al principio al soldar componentes se hizo en una habitación poco aireada y sin tapabocas o gafas.

## Cosas que haríamos mejor si se volviera a iniciar el desarrollo.
- Usar una fuente de mesa, o conseguir un transformador de USB a salidas de 5V para protoboard.
- Mejor protección a la hora de soldar.


## Siguientes implementaciones
- Control por temperatura.
- mejor aprovechamiento de la pantalla OLED.
- Pasar el código a C para mejorar el rendimiento.
- Desarrollo de una App para facilitar la conexión.
- Tratar de implementar el modo DeepSleep para reducir el consumo de energía.
- Implementar ayudas al cocinero aprovechando la pantalla OLED.
- Creación de una carcasa que se ajuste a la estufa e integre la PCB y los 4 servos.
- Planteamiento de un sistema de seguridad más eficiente.
