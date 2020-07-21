import cv2
import numpy as np
from time import sleep
import math

ancho_min=80 #Ancho minimo del retangulo
altura_min=80 #Altura minima del retangulo

offset=6 #Error permitido entre pixel  

pos_linea=550 #Posicion de la linea de conteo

delay= 60 #FPS de video (fotogramas por sgundos)

contornosReales = []
contornosAnteriores = [{
                        "centro": (0, 0),
                        "x": 0,
                        "y": 0
                        }]

carrosUp = 0
carrosDown = 0

def capturar_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx,cy

# Fuente de video
cap = cv2.VideoCapture('video.mp4')

# Substraccion de fondo
substraccion = cv2.bgsegm.createBackgroundSubtractorMOG()

while True:
    ret, frame = cap.read() # Obtener los frames del video
    tiempo = float(1/delay)
    sleep(tiempo)           #delay

    # Imagen a color
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(3,3),5)
    img_sub = substraccion.apply(blur)
    dilat = cv2.dilate(img_sub,np.ones((5,5)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilatada = cv2.morphologyEx (dilat, cv2. MORPH_CLOSE , kernel)
    dilatada = cv2.morphologyEx (dilatada, cv2. MORPH_CLOSE , kernel)

    # Contornos
    cnts = cv2.findContours(dilatada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    # Linea de cruze
    cv2.line(frame, (25, pos_linea), (1200, pos_linea), (255,127,0), 3) 

    # print('contornos: ', len(cnts))

    for c in cnts:
        (x,y,w,h) = cv2.boundingRect(c)
        validar_contorno = (w >= ancho_min) and (h >= altura_min)
        if not validar_contorno:
            continue
        # print(x,y,w,h)
                # Crear rectangulo
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
        centro = capturar_centro(x, y, w, h)
        # Detect.centro = centro

        elemento = {
            "centro": centro,
            "x": x,
            "y": y
        }
        if centro[1]<(pos_linea+offset+50) and centro[1]>(pos_linea-offset-50):
            contornosReales.append(elemento)
        
    # print('contornoReales: ', len(contornosReales))
    if(len(contornosReales)> 0):
        # for obj in contornosReales: 
        for i in range(len(contornosReales)):
            obj = contornosReales[i]
            print(obj)
            print('centro', obj['centro'][1])
            print('eje Y: ', obj['y']) 
            
            # Comparar la posición de los puntos con la posición de la linea
            if obj['centro'][1]<(pos_linea+offset) and obj['centro'][1]>(pos_linea-offset):
                obj2 = contornosAnteriores[i]
                if obj['centro'][1] > obj2['centro'][1]:
                    carrosDown+=1
                    # Cambiar de color la linea
                    cv2.line(frame, (25, pos_linea), (1200, pos_linea), (0,127,255), 3)  
                    # print("Carros detectados hasta este momento: "+str(carros))
                else:
                    carrosUp+=1
                    # Cambiar de color la linea
                    cv2.line(frame, (25, pos_linea), (1200, pos_linea), (0,127,255), 3)  
                    # print("Carros detectados hasta este momento: "+str(carros))

    print('.............................')
    print(contornosReales)
    print(contornosAnteriores)
    contornosAnteriores = contornosReales
    contornosReales = []

    # cv2.putText(frame, "VEICULOS: "+str(carros), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255),5)
    cv2.putText(frame, "DOWN: "+str(carrosDown), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255),5)
    cv2.putText(frame, "UP: "+str(carrosUp), (450, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255),5)

    cv2.imshow('Video Original',frame)
    # cv2.imshow("Detectar",dilatada)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()