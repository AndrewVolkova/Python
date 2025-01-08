# pip install opencv-python

import cv2
import time
import os
import signal
import sys

# Настройка времени, после которого блокируется экран при отсутствии пользователя перед камерой
INACTIVITY_LIMIT = 10  # в секундах

# Инициализация детектора лиц (используется каскад Хаара для детекции лиц)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Подключаем камеру
cap = cv2.VideoCapture(0)

# Время последней активности
last_activity_time = time.time()

# Функция для блокировки экрана
def block_screen():
    os.system("rundll32.exe user32.dll,LockWorkStation")

# Функция для обработки прерывания по ctrl+c (защита от неудачных завершений)
def signal_handler(sig, frame):
    print("Прерывание работы скрипта, завершение...")
    # Освобождаем ресурсы при завершении
    cap.release()  # Останавливаем камеру
    # в случае если создаем окно просмотрп изображения с камеры
    # cv2.destroyAllWindows()
    sys.exit(0)  # Завершаем выполнение

# Подключаем обработчик сигнала (например, при нажатии ctrl+c)
signal.signal(signal.SIGINT, signal_handler)

# Главный цикл
while True:
    ret, frame = cap.read()

    if not ret:
        print("Ошибка при захвате изображения с камеры.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Детектируем лица
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Проверяем наличие лиц
    if len(faces) > 0:
        last_activity_time = time.time()  # если лицо найдено, сбрасываем таймер
        print("Лицо найдено!")
    else:
        # Если не найдено лицо и прошло время ожидания без активности
        if time.time() - last_activity_time > INACTIVITY_LIMIT:
            print("Пользователь неактивен, блокируем экран...")
            block_screen()
            last_activity_time = time.time()  # сбрасываем время после блокировки

    # Убираем показ видео (не нужно отображать окно с видеопотоком)
    # cv2.imshow("Webcam", frame)

    # Обработка прерывания вручную
    time.sleep(1)  # минимальный интервал для уменьшения нагрузки на процессор

