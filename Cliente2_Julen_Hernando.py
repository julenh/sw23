# Julen Hernando Martin
import json
import os
import requests
import urllib
import sys
import csv
from bs4 import BeautifulSoup

#subprograma request reutilizable
def miRequest(cabeceras, cuerpo, metodo, uri):
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    respuesta = requests.request(metodo, uri, data=cuerpo_encoded, headers=cabeceras, allow_redirects=False)
    codigo = respuesta.status_code
    print(respuesta)
    return codigo, respuesta

def peticion1():

    metodo = 'GET'
    cabeceras = {'Host':'egela.ehu.eus'}
    cuerpo = ''
    uri = 'https://egela.ehu.eus/login/index.php'
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    return codigo,respuesta

def peticion2(moodleSession):
    metodo = 'POST'
    cabeceras = {'Host': 'egela.ehu.eus',
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'Cookie': moodleSession}
    cuerpo = {''}
    uri = 'https://egela.ehu.eus/login/index.php'
    codigo, respuesta = miRequest(cabeceras, cuerpo, metodo, uri)
    return codigo, respuesta



if __name__=="__main__":
    codigo, respuesta = peticion1()
    docParseado = BeautifulSoup(respuesta.content, "html.parser")
    docs = docParseado.find_all('div', {'class': 'signinform'})
    docs1 = docParseado.find('form', {'class': 'm-t-1 ehuloginform'})
    redirect = docs1.get('action')
    docs2 = docParseado.find('input', {'name': 'logintoken'})
    logintoken = docs2.get('value')
    print(codigo)
    print(respuesta.headers['Set-Cookie'])
    print(docs2)
    print(logintoken)
