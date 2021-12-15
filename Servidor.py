from flask import Flask, jsonify, request, make_response
import base64
import cv2
from io import BytesIO
import numpy as np
from PIL import Image
from Prediccion import Prediccion
import os


app = Flask(__name__)

clases = ["2 mil", "5 mil", "10 mil", "20 mil", "50 mil"]
ancho = 256
alto = 256

@app.route('/')
def saludo():
    return "Buenos días"

@app.route('/predict', methods=['POST'])
def predict():
    resp = None
    rslts = []
    peticion = {
        'id_client':  request.json['id_client'],
        'images': request.json['images'],
        'models': request.json['models']
    }
    convrt = decodeBase64(peticion['images'])
    if convrt:
        try:
            billetes = listarBilletes('ServerFolder/Billetes')
            for model in peticion['models']:
                modeloCNN = initPredict(ancho, alto, model)
                idImg = 0
                resultado = []
                for imagen in billetes:
                    if '.jpg' in imagen:
                        img = cv2.imread("ServerFolder/Billetes/"+imagen)
                        index = modeloCNN.predecir(img)
                        resultado.append({'class': clases[index], 'id_image': idImg})
                        idImg += 1
                rslts.append({'model_id': model, 'results': resultado})
            response = {
                'state': 'success',
                'message': 'Predictions made satisfactorily',
                'results': rslts
            }
            response = jsonify(response)
            resp = make_response(response)
            resp.status_code = 200
            resp.headers['Content-Type'] = 'application/json'
            resp.content_type = 'application/json'
        except Exception as e:
            response = {
                'state': 'error',
                'message': 'Error making predictions'
            }
            response = jsonify(response)
            resp = make_response(response)
            resp.status_code = 400
            resp.headers['Content-Type'] = 'application/json'
            resp.content_type = 'application/json'
    elif not convrt:
        response = {
            'state': 'error',
            'message': 'Error making predictions'
        }
        response = jsonify(response)
        resp = make_response(response)
        resp.status_code = 400
        resp.headers['Content-Type'] = 'application/json'
        resp.content_type = 'application/json'

    return resp

def decodeBase64(codeImage):
    id = 0
    try:
        for image in codeImage:
            sbuf = BytesIO()
            sbuf.write(base64.b64decode(image['content']))
            pimg = Image.open(sbuf)
            img = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
            cv2.imwrite('ServerFolder/Billetes/billete'+str(image['id'])+'.jpg', img)
            id+=1
        return True
    except Exception as e:
        return False

def initPredict(ancho,alto,modelo):
    if modelo == "1": modelo = "modeloA.h5"
    if modelo == "2": modelo = "modeloB.h5"
    if modelo == "3": modelo = "modeloC.h5"
    miModeloCNN = Prediccion("ServerFolder/models/"+modelo, ancho, alto)
    return miModeloCNN

def listarBilletes(ruta):
    dir = ruta
    imagenes = []
    with os.scandir(dir) as ficheros:
        for fichero in ficheros:
            imagenes.append(fichero.name)
    return imagenes

if __name__ == '__main__':
    app.run(debug=True, port=8069)
