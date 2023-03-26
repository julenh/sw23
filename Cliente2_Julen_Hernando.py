# Julen Hernando Martin
import json
import os
import requests
import urllib
import sys
import csv
from bs4 import BeautifulSoup
import getpass

#usuario
user = sys.argv[1]
nombreUsuario = sys.argv[2]
#contraseña
password = ''

#subprograma request reutilizable
def post(cabeceras, cuerpo, uri):
    metodo = 'POST'
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    respuesta = requests.request(metodo, uri, data=cuerpo_encoded, headers=cabeceras, allow_redirects=False)
    codigo = respuesta.status_code
    print(respuesta)
    return codigo, respuesta

def get(cabeceras,  uri):
    metodo = 'GET'
    cuerpo_encoded = urllib.parse.urlencode('')
    respuesta = requests.request(metodo, uri, data=cuerpo_encoded, headers=cabeceras, allow_redirects=False)
    codigo = respuesta.status_code
    print(respuesta)
    return codigo, respuesta
#Peticion para obtener la primera cookie y el logintoken
def peticion1():
    cabeceras = {'Host':'egela.ehu.eus'}
    uri = 'https://egela.ehu.eus/login/index.php'
    codigo, respuesta = get(cabeceras, uri)
    return codigo,respuesta

#peticion 2 de inicio de sesion para obtener la testsession y la cookie
def peticion2(uri, moodleSession, lToken):
    cabeceras = {'Host': 'egela.ehu.eus',
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'Cookie': moodleSession}
    cuerpo = {'logintoken':lToken, 'username': user, 'password': password}
    uri = 'https://egela.ehu.eus/login/index.php'
    codigo, respuesta = post(cabeceras, cuerpo, uri)
    return codigo, respuesta

#peticion 3 para obtener la redireccion
def peticion3(uri, moodleSession):
    cabeceras = {'Host': 'egela.ehu.eus',
                 'Cookie': moodleSession}
    codigo, respuesta = get(cabeceras, uri)
    return codigo, respuesta

#peticion 4, acceso definitivo a egela
def peticion4(uri, moodleSession):
    cabeceras = {'Host': 'egela.ehu.eus',
                 'Cookie': moodleSession}
    codigo, respuesta = get(cabeceras, uri)
    return codigo, respuesta

def obtenerEnlaces(enlaceAsignatura, cookie):
    codigo, respuesta = peticion4(enlaceAsignatura, cookie)
    htmlSW = BeautifulSoup(respuesta.content, "html.parser")
    # encontrar pdf y entregas
    indicesPDF = htmlSW.find_all('img', {'class': 'iconlarge activityicon'})
    enlacesPDF = []
    enlacesEntregas = []
    for i in indicesPDF:
        if "pdf" in str(i):
            enlacesPDF.append(i.parent['href'])
        if "assign" in str(i):
            if "href" in str(i.parent):
                enlacesEntregas.append(i.parent['href'])
    return enlacesPDF, enlacesEntregas

def guardarPDF(enlacesPDF, cookie):
    for i in enlacesPDF:
        codigo, respuesta = peticion4(i, cookie)
        if codigo == 303:
            location = respuesta.headers['Location']
            codigo, respuesta = peticion4(location, cookie)

            if codigo == 200:
                nombrePDF = location.split("/").pop()
                os.makedirs("pdf", exist_ok=True)
                archivo = open("./pdf/"+nombrePDF, "wb")
                archivo.write(respuesta.content)
                archivo.close()

def guardarVSV(enlacesEntregas, cookie):
    titulo = []
    fecha = []
    for i in enlacesEntregas:
        codigo, respuesta = peticion4(i, cookie)
        html = BeautifulSoup(respuesta.content, "html.parser")
        temp = html.findAll('td', {'class': 'cell c1 lastcol'})
        titulo.append(html.find('h2').text)
        for j in temp:
            if "2023" in str(j) or "2022" in str(j):
                fecha.append(j.text)
    with open('Entregas Sistemas Web', 'w', newline='') as csvfile:
        fieldNames = ['Titulo', 'fecha de entrega', 'enlace']
        fileWriter = csv.DictWriter(csvfile, fieldnames=fieldNames, delimiter=';')
        for k in range(len(enlacesEntregas)):
            row = {'Titulo': titulo[k],
                   'fecha de entrega': fecha[k],
                   'enlace': enlacesEntregas[k]}
            fileWriter.writerow(row)






if __name__=="__main__":
    #se pide la contrasena
    password = getpass.getpass('Password:')
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
    location = respuesta2.headers['Location']
    cookie = respuesta2.headers['Set-Cookie'].split(';')[0]

    #datos obtenidos de la peticion 2
    print("autenticacion correcta")
    print("datos obtenidos de la peticion 2")
    print("redireccion a: "+location)
    print("cookie de la peticion 2: "+cookie)

    #peticion 3
    codigo3, respuesta3 = peticion3(location, cookie)
    location = respuesta3.headers['Location']
    #redireccion obtenida de la peticion 3
    print("datos de la peticion 3")
    print("redireccion a: "+location)
    #print("cookie de la peticion 3: "+cookiePeti2)

    # peticion 4
    codigo, respuesta = peticion4(location,cookie )
    print(codigo)
    #print(respuesta.text)
    print("------------")

    #obtener asignatura
    html2 =  BeautifulSoup(respuesta.content, "html.parser")
    asignaturas = html2.findAll('a', {'class': 'ehu-visible'})
    for i in asignaturas:
        if "Sistemas Web" in str(i):
            redirectSW = i.get('href')

    #peticion y obtencion de pdf y entregas Sistemas web
    print("obteniendo pdf y datos de entregas")
    enlacesPDF, enlacesEntregas = obtenerEnlaces(redirectSW, cookie)

    #guardar PDF
    print("guardando pdf")
    guardarPDF(enlacesPDF, cookie)

    #csv de entregas
    print("guardando datos de entregas")
    guardarVSV(enlacesEntregas, cookie)








