#Julen Hernando Martin
import json
import os
import signal
import sys
import urllib.parse
import requests
import psutil
import time

user_API_key = "5N5KQVAFEADQ22VA"
nombreCanal = "Mi Canal"
idCanal = ""
write_API_key = "YPIWPJK1HX135LJW"
datosCanal = {}
#Lectura de CPU y RAM
def cpu_ram():
    return psutil.cpu_percent(), psutil.virtual_memory().percent

#subprograma handler
def handler(sig_num, frame):
    print('\nSignal handler called with signal ' + str(sig_num))
    print('\nExiting gracefully')
    sys.exit()
#subprograma request reutilizable
def miRequest(cabeceras, cuerpo, metodo, uri):
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    respuesta = requests.request(metodo, uri, data=cuerpo_encoded, headers=cabeceras, allow_redirects=False)
    codigo = respuesta.status_code
    print(respuesta)
    return codigo, respuesta

#crear canal en thingspeak
def crearCanal(user_API_key):
    metodo = 'POST'
    uri = "https://api.thingspeak.com/channels.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': user_API_key,
              'name': 'Mi Canal',
              'field1': "%CPU",
              'field2': "%RAM"}
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    #si la conexion es correcta
    if(codigo == 200):
        print("canal creado con exito")
        contenido = respuesta.content.decode()
        datosCanal = json.loads(contenido)
        return datosCanal
    else:
        print("se ha producido un error al crear el canal")
if __name__ == "__main__":
    print(crearCanal(user_API_key))
    #cpu_ram()
   # while True:
    #    print(cpu_ram())
     #   time.sleep(5)
