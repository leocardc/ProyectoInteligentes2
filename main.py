import cv2
import time

import numpy as np
import base64
import os
import requests
import json

nameWindow="Calculadora Canny"
class Cut:
    # function to crop image
    # Parameters: image to crop, contour, and the image number
    def crop(image, contours, num, bordes):
        pru = image
        new_img = bordes
        idNum = num

        # cycles through all the contours to crop all
        for c in contours:
            area = cv2.contourArea(c)
            if area == 0:
                break
            # creates an approximate rectangle around contour
            x, y, w, h = cv2.boundingRect(c)
            # Only crop decently large rectangles
            # cv2.imshow("Bordes", imagen)
            # if( w>100 and h>100):
            #     print('w',w)
            #     print('h',h)
            if (w > 370 and h > 180) or (h > 370 and w > 180):
                # print("w es %s y h es %s" %(w,h))
                # cv2.drawContours(pru, [c], 0, (0, 255, 255), 2)
                cv2.imshow("Recorte", imagen)
                # print("Oprima c para recortar")
                new_img = bordes[y:y + h, x:x + w]
                if cv2.waitKey(1) & 0xFF == ord('c'):
                    # pulls crop out of the image based on dimensions
                    idNum += 1
                    # writes the new file in the Crops folder
                    cv2.imwrite('Crops/' + 'billete_' + str(idNum) +
                                '.jpg', new_img)
                    print("Se tomó el recorte")


        # returns a number incremented up for the next file name
        return idNum, new_img
def nothing(x):
    pass
def constructorVentana():
    cv2.namedWindow(nameWindow)
    cv2.createTrackbar("min",nameWindow,170,500,nothing)
    cv2.createTrackbar("max", nameWindow, 255, 1000, nothing)
    cv2.createTrackbar("kernel", nameWindow, 2, 100, nothing)
    cv2.createTrackbar("areaMin", nameWindow, 67500, 200000, nothing)
    cv2.createTrackbar("areaMax", nameWindow, 200000, 300000, nothing)

#calcylar area de la fugura
def calcularAreas(figuras):
    areas = []
    for figuraActual in figuras:
        areas.append(cv2.contourArea(figuraActual))
    return areas

def detectarFormas(imagen,idImg):
    billete = imagen
    imagengris = cv2.cvtColor(imagen,cv2.COLOR_RGB2GRAY)
    min = cv2.getTrackbarPos("min", nameWindow)
    max = cv2.getTrackbarPos("max", nameWindow)
    tamañoKernel = cv2.getTrackbarPos("kernel", nameWindow)
    areamin = cv2.getTrackbarPos("areaMin", nameWindow)
    areamax = cv2.getTrackbarPos("areaMax", nameWindow)
    bordes = cv2.Canny(imagengris, min, max)
    kernel = np.ones((tamañoKernel, tamañoKernel), np.uint8)
    bordes = cv2.dilate(bordes, kernel)
    # cv2.imshow('Imagen', bordes)
    contornosR, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    kernel = np.ones((tamañoKernel, tamañoKernel), np.uint8)
    bordes = cv2.dilate(bordes, kernel)
    cnts,_ = cv2.findContours(bordes,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow('Imagen2', bordes)
    areas = calcularAreas(cnts)
    i = 0
    for figuraActual in cnts:
        area = cv2.contourArea(figuraActual)
        if area >= areamin and area <= areamax:
            # cv2.drawContours(billete, [figuraActual], 0, (0, 0, 255), 2)
            # cv2.imshow('bordes', billete)
            epsilon = 0.01 * cv2.arcLength(figuraActual, True)
            approx = cv2.approxPolyDP(figuraActual, epsilon, True)
            x, y, w, h = cv2.boundingRect(approx)
            # coordenadas de los vertices
            vertices = cv2.approxPolyDP(figuraActual, epsilon, True)

            if len(vertices) == 4:
                aspect_ratio = float(w) / h
                if aspect_ratio == 1:
                    cv2.putText(imagen, 'Cuadrado', (x, y - 5), 1, 1.5, (0, 255, 0), 2)
                else:

                    # print("recorte")
                    # cv2.putText(imagen, 'rect', (x, y - 5), 1, 1.5, (0, 255, 0), 2)
                    idImg, imagen = recorte.crop(billete, cnts, idImg, bordes)
        i+=1
    return billete, idImg

def cnvrtBase64(rutaImagen):
    img = cv2.imread(rutaImagen)
    retval, buffer = cv2.imencode('.jpg',img)
    jpg_as_text = base64.b64encode(buffer)
    encoded_string = jpg_as_text.decode('utf-8')
    return encoded_string

#Función para devolver los nombres de las imagenes obtenidas
def listarBilletes(ruta):
    dir = ruta
    imagenes = []
    with os.scandir(dir) as ficheros:
        for fichero in ficheros:
            imagenes.append(fichero.name)
    return imagenes

camara = cv2.VideoCapture(1)


recorte = Cut
k = 0
#Identificación del cliente
idcliente = input('Ingrese un identificador: ')
cantModelos = input('Ingrese la cantidad de modelos que desea usar: ')
modelos = []
if cantModelos == "1" or cantModelos == "2" or cantModelos == "3":
    for i in range(int(cantModelos)):
        modelos.append(input('Ingrese el número de modelo "Para el modelo A 1, modelo B 2, modelo C 3": '))
        if modelos[i] != "1" and modelos[i] != "2" and modelos[i] != "3":
            print('No ingresó un modelo válido')
            exit()
else:
    print('No ingresó una cantidad de modelos válido')
    exit()
constructorVentana()
idImg = 0
while True:
    k = cv2.waitKey(1)
    _,imagen = camara.read()

    imagen,idImg = detectarFormas(imagen,idImg)
    cv2.imshow('Imagen', imagen)
    if k == ord('e'):
        break

#Inicio el envío de las imagenes al servidor 'Crops/billete_n.jpg'
imgBase64 = []
billetes = listarBilletes('Crops')
# print(billetes)
idsImg = 0
for imgBillete in billetes:
    imageBase64 = cnvrtBase64('Crops/' + imgBillete)
    imgBase64.append({"id":idsImg,"content":imageBase64})
    idsImg+=1
data = {'id_client': idcliente, 'images': imgBase64, 'models': modelos}
headers = {'Content-Type': 'application/json'}
resp = requests.post('http://localhost:8069/predict', data=json.dumps(data), headers=headers)
respuesta = json.loads(resp.text)
print(respuesta)