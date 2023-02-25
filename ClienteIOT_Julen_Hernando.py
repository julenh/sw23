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
API_key_w = "R5JNSRLBTLDNLL3N"
API_key_r = "HPNS4GGMJOR7EFCR"
#Lectura de CPU y RAM
def cpu_ram():
    return psutil.cpu_percent(), psutil.virtual_memory().percent

#subprograma handler
def handler(sig_num, frame):
    print('\nSignal handler called with signal ' + str(sig_num))
    leerCanal(idCanal, API_key_r)
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
    cuerpo = {'api_key': user_API_key}
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
    with open('MiCanal.csv', 'w', newline='') as csvfile:
        field_names = ['timestamp', 'cpu', 'ram']
        filewriter = csv.DictWriter(csvfile, fieldnames=field_names, delimiter=';')
        #filewriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        #filewriter.writerow(['Timestamp', 'CPU', 'RAM'])
        if(len(feeds) < 100):
            for i in feeds:
                row = {'timestamp': i['created_at'],
                       'cpu': i['field1'],
                       'ram': i['field2']}
                filewriter.writerow(row)
        else:
            for i in range(100):
                row = {'timestamp': i['created_at'],
                       'cpu': i['field1'],
                       'ram': i['field2']}
                filewriter.writerow(row)

# Vaciar los datos del canal (con user_API_key)
def vaciarCanal(idCanal, API_key):
    print("Vaciar datos del canal")
    metodo = 'DELETE'
    uri = "https://api.thingspeak.com/channels/"+str(idCanal)+"/feeds.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': API_key}
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    miRequest(cabeceras, cuerpo, metodo, uri)


if __name__ == "__main__":

    datosCanal = comprobarCanales()
    existe = False
    for i in range(len(datosCanal)):
        if(datosCanal[i]['name'] == nombreCanal):
            canal = datosCanal[i]
            print("Existe canal "+nombreCanal)
            existe = True
            break

    if(existe == False):
        if(len(datosCanal) == 4):
            print("No se pueden crear mas canales")
            print("Borra alguno de los canales")
        else:
            print("No existe canal "+nombreCanal)
            canal = crearCanal(user_API_key)
            existe = True

    if(existe == True):
        print("Existe Canal")
        idCanal = canal['id']
        #nombreCanal = canal['name']
        API_key_w = canal['api_keys'][0]['api_key']
        API_key_r = canal['api_keys'][1]['api_key']
        print(API_key_w)
        print(API_key_r)
        signal.signal(signal.SIGINT, handler)
        while True:
            subirDatos(API_key_w)
            time.sleep(5)
