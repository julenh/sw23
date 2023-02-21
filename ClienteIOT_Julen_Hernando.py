#Julen Hernando Martin
import json
import os
import signal
import sys
import urllib.parse
import requests
import psutil
import time
import csv

user_API_key = "5N5KQVAFEADQ22VA"
nombreCanal = "Mi Canal"
idCanal = ""
API_key = "YPIWPJK1HX135LJW"
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
        return ""

def subirDatos(api_key):
    print("subida de datos")
    cpu, ram = cpu_ram()
    metodo = 'POST'
    uri = "https://api.thingspeak.com/update.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': api_key, 'field1': cpu, 'field2': ram}
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    miRequest(cabeceras, cuerpo, metodo, uri)

def comprobarCanales():
    print("comprobando que canales existen")
    metodo = 'GET'
    uri = "https://api.thingspeak.com/channels.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_keyt': user_API_key}
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    contenido = respuesta.content
    return json.loads(contenido)

def leerCanal(idCanal, API_key):
    print("Obteniendo datos del canal")
    metodo = 'GET'
    uri = "https://api.thingspeak.com/channels/"+ str(idCanal) + "/feeds.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': API_key}
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    if (codigo == 200):
        print("Acceso correcto")
        contenido = respuesta.content
        datosCanal = json.loads(contenido)
        # guardar datos del canal
        guardarDatos(datosCanal["feeds"])
    else:
        print("Error al obtener datos del canal")

#guardar los datos en un csv
def guardarDatos(feeds):
    print("Guardando datos en un csv")
    with open('MiCanal.csv', 'wb') as csvfile:
        filewriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        filewriter.writerow(['Timestamp', 'CPU', 'RAM'])
        for i in range(len(feeds)):
            filewriter.writerow([feeds[i]['created_at'], feeds[i]['field1'], feeds[i]['field2']])


if __name__ == "__main__":
    #print(crearCanal(user_API_key))
    #cpu_ram()
    leerCanal("2037008", "HPNS4GGMJOR7EFCR")
    while True:
        subirDatos("R5JNSRLBTLDNLL3N")
    #    print(cpu_ram())
        time.sleep(5)
