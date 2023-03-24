# Julen Hernando Martin
import json
import os
import requests
import urllib
import sys
import csv
from bs4 import BeautifulSoup

#usuario
user = '775473'
#contraseña
password = 'Ragnarok12_a'

#subprograma request reutilizable
def miRequest(cabeceras, cuerpo, metodo, uri):
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    respuesta = requests.request(metodo, uri, data=cuerpo_encoded, headers=cabeceras, allow_redirects=False)
    codigo = respuesta.status_code
    print(respuesta)
    return codigo, respuesta

#Peticion para obtener la primera cookie y el logintoken
def peticion1():

    metodo = 'GET'
    cabeceras = {'Host':'egela.ehu.eus'}
    cuerpo = ''
    uri = 'https://egela.ehu.eus/login/index.php'
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    return codigo,respuesta

#peticion 2 de inicio de sesion para obtener la testsession y la cookie
def peticion2(uri, moodleSession, lToken):
    metodo = 'POST'
    cabeceras = {'Host': 'egela.ehu.eus',
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'Cookie': moodleSession}
    cuerpo = {'logintoken':lToken, 'username': user, 'password': password}
    uri = 'https://egela.ehu.eus/login/index.php'
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    return codigo, respuesta

#peticion 3 para obtener la redireccion
def peticion3(uri, moodleSession):
    metodo = 'GET'
    cabeceras = {'Host': 'egela.ehu.eus',
                 'Cookie': moodleSession}
    cuerpo = ''

    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    return codigo, respuesta

#peticion 4, acceso definitivo a egela
def peticion4(uri, moodleSession):
    metodo = 'GET'
    cabeceras = {'Host': 'egela.ehu.eus',
                 'Cookie': moodleSession}
    cuerpo = ''
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    return codigo, respuesta



if __name__=="__main__":
    #se hace la primera peticion
    codigo, respuesta = peticion1()
    #obtener cookie
    cookie = respuesta.headers['Set-Cookie'].split(';')[0]
    #parsear html y obtener enlace y logintoken
    peti1Html = BeautifulSoup(respuesta.content, "html.parser")
    docs1 = peti1Html.find('form', {'class': 'm-t-1 ehuloginform'})
    redirectPeti1 = docs1.get('action')
    docs2 = peti1Html.find('input', {'name': 'logintoken'})
    logintoken = docs2.get('value')
    #datos obtenidos de la peticion 1
    print("datos obtenidos de la peticion 1")
    print("redireccion a: "+redirectPeti1)
    print("cookie de la peticion 1: "+cookie)
    print("logintoken: "+logintoken)
    #peticion2
    codigo2, respuesta2 = peticion2(redirectPeti1, cookie, logintoken)
    redirectPeti2 = respuesta2.headers['Location']
    cookiePeti2 = respuesta2.headers['Set-Cookie'].split(';')[0]
    #datos obtenidos de la peticion 2
    print("datos obtenidos de la peticion 2")
    print("redireccion a: "+redirectPeti2)
    print("cookie de la peticion 2: "+cookiePeti2)
    #peticion 3
    codigo3, respuesta3 = peticion3(redirectPeti2, cookiePeti2)
    redirectPeti3 = respuesta3.headers['Location']
    #redireccion obtenida de la peticion 3
    print("datos de la peticion 3")
    print("redireccion a: "+redirectPeti3)
    print("cookie de la peticion 3: "+cookiePeti2)

    codigo4, respuesta4 = peticion4(redirectPeti3, cookiePeti2)
    peti4Html = BeautifulSoup(respuesta.content, "html.parser")
    print(peti4Html)






