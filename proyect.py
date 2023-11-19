import cv2
import numpy as np
import keyboard

# Inicializa la cámara
cap = cv2.VideoCapture(0)

# Establece los valores umbral para la detección del color de la mano (ajústalos según sea necesario)
lower_skin = np.array([0, 20, 70], dtype=np.uint8)
upper_skin = np.array([20, 255, 255], dtype=np.uint8)

# Inicializa la variable de volumen
volume = 0

# Define las coordenadas de los bloques superior e inferior
upper_block = (0, 0, int(cap.get(3)), int(cap.get(4) / 2))  # (x, y, width, height)
lower_block = (0, int(cap.get(4) / 2), int(cap.get(3)), int(cap.get(4) / 2))


while True:
    # Captura el video de la cámara
    ret, frame = cap.read()

    # Convierte el frame a espacio de color HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Filtra la piel utilizando el rango definido
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Encuentra los contornos de la mano
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Encuentra el contorno más grande (suponemos que es la mano)
        hand_contour = max(contours, key=cv2.contourArea)

        # Encuentra el centro de la mano
        M = cv2.moments(hand_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Verifica si el dedo está en el bloque superior
            if cy < upper_block[3]:
                volume = int(np.interp(cx, [0, frame.shape[1]], [0, 100]))
            # Verifica si el dedo está en el bloque inferior
            elif cy > lower_block[1]:
                volume = int(np.interp(cx, [0, frame.shape[1]], [100, 0]))

            # Ajusta el volumen
            keyboard.press_and_release('volume down' if volume < 50 else 'volume up')

        # Dibuja el contorno de la mano y el centro en el frame
        cv2.drawContours(frame, [hand_contour], 0, (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

    # Dibuja los bloques en el frame
    cv2.rectangle(frame, (upper_block[0], upper_block[1]), (upper_block[0] + upper_block[2], upper_block[1] + upper_block[3]), (0, 0, 255), 2)
    cv2.rectangle(frame, (lower_block[0], lower_block[1]), (lower_block[0] + lower_block[2], lower_block[1] + lower_block[3]), (0, 0, 255), 2)


    # Muestra el frame con el resultado
    cv2.imshow("Hand Tracking", frame)

    # Espera a la tecla 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera la cámara y cierra las ventanas
cap.release()
cv2.destroyAllWindows()
