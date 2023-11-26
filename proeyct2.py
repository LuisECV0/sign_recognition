import cv2
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time

# Inicializar el módulo de MediaPipe para el seguimiento de manos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Configurar la cámara
cap = cv2.VideoCapture(0)

# Coordenadas de los botones
button_coordinates = [(30, 30), (90, 30), (150, 30), (210, 30), (270, 30), (330, 30), (390, 30), (450, 30), (510, 30), (570, 30),
                      (630, 30)]  # Coordenadas del botón de salida

# Volumen inicial
volume = 0

# Inicializar variables para el cambio de tamaño de la ventana
window_size = (1280, 720)
resized = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Invertir horizontalmente el frame para deshacernos del efecto espejo
    frame = cv2.flip(frame, 1)

    # Cambiar el tamaño de la ventana si es necesario
    if resized:
        frame = cv2.resize(frame, window_size)

    # Convertir el frame a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar manos en el frame
    results = hands.process(frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Dibujar líneas rectas entre los puntos de la mano
            for i in range(len(hand_landmarks.landmark) - 1):
                x1, y1 = int(hand_landmarks.landmark[i].x * frame.shape[1]), int(hand_landmarks.landmark[i].y * frame.shape[0])
                x2, y2 = int(hand_landmarks.landmark[i + 1].x * frame.shape[1]), int(hand_landmarks.landmark[i + 1].y * frame.shape[0])
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Dibujar puntos rojos solo en la punta de los dedos
            touched_buttons = set()
            for finger_tip_id in [4, 8, 12, 16, 20]:  # Índices correspondientes a las puntas de los dedos
                x, y = int(hand_landmarks.landmark[finger_tip_id].x * frame.shape[1]), int(
                    hand_landmarks.landmark[finger_tip_id].y * frame.shape[0])

                # Verificar si se toca un botón
                for i, button_coord in enumerate(button_coordinates):
                    button_x, button_y = button_coord
                    if button_x - 20 < x < button_x + 20 and button_y - 20 < y < button_y + 20:
                        touched_buttons.add(i)

            if len(touched_buttons) == 1:
                # Ajustar el volumen solo si se toca un solo botón
                button_index = list(touched_buttons)[0]
                volume = button_index * 10

                # Ajustar el volumen usando la biblioteca pycaw
                try:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(
                        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume_object = cast(interface, POINTER(IAudioEndpointVolume))
                    volume_object.SetMasterVolumeLevelScalar(volume / 100, None)
                except Exception as e:
                    print(f"Error ajustando el volumen: {e}")

                time.sleep(0.1)  # Añadir una pequeña pausa

                # Agregar animación: dibujar un círculo alrededor del botón presionado
                button_x, button_y = button_coordinates[button_index]
                cv2.circle(frame, (button_x, button_y), 25, (0, 0, 255), -1)

    # Dibujar los botones
    for button_coord in button_coordinates:
        button_x, button_y = button_coord
        cv2.rectangle(frame, (button_x - 20, button_y - 20), (button_x + 20, button_y + 20), (255, 0, 0), -1)
        cv2.putText(frame, str(button_coordinates.index(button_coord) * 10), (button_x - 10, button_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Mostrar el volumen actual
    cv2.putText(frame, f"Volume: {volume}%", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Mostrar el resultado
    cv2.imshow("Hand Tracking", frame)

    # Manejar eventos de teclado
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        resized = not resized  # Cambiar el estado de cambio de tamaño de la ventana

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
