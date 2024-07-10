import datetime
import string
import tkinter as tk
import time
import paho.mqtt.client as mqtt
import random
import string

# Функция, вызываемая при подключении к брокеру MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Подписываемся на темы для получения команд
    client.subscribe("home/calibrate")
    client.subscribe("home/close")
    client.subscribe("home/open")
    client.subscribe("home/сopcontrol_illuminationen")
    client.subscribe("home/control_temperature")
    client.subscribe("home/value")

# Функция, вызываемая при получении сообщения от брокера MQTT
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # Проверяем тему и выполняем соответствующие действия
    if msg.topic == "home/calibrate":
        calibrate()
    elif msg.topic == "home/close":
        set_closing_time()
    elif msg.topic == "home/open":
        set_opening_time()
    elif msg.topic == "home/control_illumination":
        update_illumination_scale()
    elif msg.topic == "home/control_temperature":
        update_illumination_scale()
    elif msg.topic == "home/value":
        scale.set(scale_value)
    else:
        print("Получена неизвестная команда.")


# Функция, вызываемая при отправке сообщения брокеру MQTT
def publish(topic, data):
    try:
        # Проверяем, активно ли подключение к брокеру MQTT
        if not client.is_connected():
            # Если не подключены, подключаемся
            client.connect(broker_address, broker_port, 1883)

        # Получаем данные для освещённости и температуры
        illumination_label = entry_1.get()
        temperature_label = entry_2.get()

        # Получаем данные о положении шторы
        value = scale_value

        # Отправляем данные
        client.publish("home/control_illumination", illumination_label)
        print("Данные об уровне освещённости отправлены.")

        client.publish("home/control_temperature", temperature_label)
        print("Данные об уровне температуры отправлены.")

        client.publish("home/value", value)
        print("Данные о положении шторы отправлены.")

    except Exception as e:
        print("Ошибка при отправке данных: ", e)


# Значение ползунка от значения освещённости
def update_illumination_scale(*args):
    try:
        illumination_level = float(entry_1.get())
        if 0 <= illumination_level <= 100:
            scale.set(illumination_level)

        else:
            print("Ошибка: Уровень освещённости должен быть от 0 до 100.")
    except ValueError:
        print("Ошибка: Введите корректное число для уровня освещённости.")

# Значение ползунка от значения температуры
def update_temperature_scale(*args):
    try:
        temperature_level = float(entry_2.get())
        if 20 <= temperature_level <= 23:
            temperature_scale = 50
            scale.set(temperature_scale)
        elif temperature_level >= 24:
            scale.set(scale.cget('to'))
        else:
            scale.set(scale.cget('from'))

    except ValueError:
        print("Ошибка: Введите корректное число для уровня температуры.")


# Калибровка ползунка
def calibrate():
    root.after(1000, lambda: scale.set(scale.cget('from')))     # Перемещение в крайнее левое положение
    root.after(2000, lambda: scale.set(scale.cget('to')))       # Перемещение в крайнее правое положение
    root.after(3000, lambda: scale.set(scale.cget('from')))


# Часы
def tick():
    clock['text'] = time.strftime("%H:%M:%S")
    clock.after(1000, tick)


# Закрытие шторы по времени
def set_closing_time():
    def process_closing_time(entry):
        closing_time_top = entry.get()
        try:
            closing_time = datetime.datetime.strptime(closing_time_top, "%H:%M")
            current_time = datetime.datetime.now().time()

            # Получение времени из datetime.datetime
            closing_time = closing_time.time()

            if closing_time > current_time:
                # Определение времени до выполнения действия в миллисекундах
                time_difference = (datetime.datetime.combine(datetime.datetime.now().date(), closing_time) -
                                   datetime.datetime.now()).total_seconds() * 1000

                # Запуск перемещения ползунка через определенное время
                root.after(int(time_difference), lambda: scale.set(scale["to"]))
                print("Шторы закроются по расписанию.")
            else:
                print("Указанное время уже прошло.")
        except ValueError:
            print("Некорректный формат времени. Используйте HH:MM.")


    # Создаем дополнительное окно Toplevel
    top = tk.Toplevel(root)

    label = tk.Label(top, text="Введите время в формате HH:MM.")
    label.pack(pady=10)

    entry = tk.Entry(top)
    entry.pack(pady=10)

    button = tk.Button(top, text="Закрыть шторы в указанное время", command=lambda: process_closing_time(entry))
    button.pack(pady=10)


# Открытие шторы по времени
def set_opening_time():
    def process_opening_time(entry):
        opening_time_top = entry.get()
        try:
            opening_time = datetime.datetime.strptime(opening_time_top, "%H:%M")
            current_time = datetime.datetime.now().time()

            # Получение времени из datetime.datetime
            opening_time = opening_time.time()

            if opening_time > current_time:
                # Определение времени до выполнения действия в миллисекундах
                time_difference = (datetime.datetime.combine(datetime.datetime.now().date(), opening_time) -
                                   datetime.datetime.now()).total_seconds() * 1000

                # Запуск перемещения ползунка через определенное время
                root.after(int(time_difference), lambda: scale.set(scale["from"]))
                print("Шторы откроются по расписанию.")
            else:
                print("Указанное время уже прошло.")
        except ValueError:
            print("Некорректный формат времени. Используйте HH:MM.")

    # Создаем дополнительное окно Toplevel
    top = tk.Toplevel(root)

    label = tk.Label(top, text="Введите время в формате HH:MM.")
    label.pack(pady=10)

    entry = tk.Entry(top)
    entry.pack(pady=10)

    button = tk.Button(top, text="Открыть шторы в указанное время", command=lambda: process_opening_time(entry))
    button.pack(pady=10)


# Создаём секретный ключ
def secret_key(length):
    all_symbols = string.ascii_uppercase + string.digits
    result = ''.join(random.choice(all_symbols) for _ in range(length))
    return result

# Генерация секретного ключа один раз при запуске программы
try:
    key = secret_key(10)
except ValueError as e:
    key = str(e)

# Создаём главное окно
root = tk.Tk()
root.title("Эмулятор умного устройства")

# Настройка MQTT клиента
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Указание адреса и порта брокера MQTT и подключение к нему
broker_address = "5.23.53.69"
broker_port = 1883
client.connect(broker_address, broker_port, 60)

# Запуск цикла работы MQTT клиента
client.loop_start()

# Создаём часы
clock = tk.Label(root, font=('Arial', 13))

# Датчик освещённости
illumination_label = tk.Label(text="Уровень освещённости (от 0 до 100): ")
entry_1 = tk.Entry()

# Датчик температуры
temperature_label = tk.Label(text="Уровень температуры (в градусах Цельсия): ")
entry_2 = tk.Entry()

# Секретный ключ
secret_key = tk.Label(root, text="Секретный ключ: "+ key)

# Создаём кнопки
label = tk.Label(text="Настройки автоматизации: ")
btn_1 = tk.Button(root, text="Калибровка", command=calibrate)
btn_2 = tk.Button(root, text="Закрытие штор по времени", command=set_closing_time)
btn_3 = tk.Button(root, text="Открытие штор по времени", command=set_opening_time)
btn_4 = tk.Button(root, text="Регулировка в зависимости от освещённости", command=update_illumination_scale)
btn_5 = tk.Button(root, text="Регулировка в зависимости от температуры", command=update_temperature_scale)
btn_6 = tk.Button(root, text="Отправить данные", command=lambda: publish(entry_1, entry_2))

# Создаём ползунок
scale_value = tk.DoubleVar()
scale = tk.Scale(root, orient=tk.HORIZONTAL, length=200, from_=1.0, to=100.0, variable=scale_value)
scale.set(0)

# Располагаем элементы с использованием grid
illumination_label.grid(row=2, column=0, sticky="s")
entry_1.grid(row=3, column=0, sticky="n")
temperature_label.grid(row=4, column=0, sticky="s")
entry_2.grid(row=5, column=0, sticky="n")
btn_6.grid(row=6, column=0, sticky="n", pady=5)
clock.grid(row=7, column=0, padx=5)
label.grid(row=0, column=2, rowspan=2, padx=10)
btn_1.grid(row=2, column=2, sticky="ew", pady=5)
btn_2.grid(row=3, column=2, sticky="ew", pady=5)
btn_3.grid(row=4, column=2, sticky="ew", pady=5)
btn_4.grid(row=5, column=2, sticky="ew", pady=5)
btn_5.grid(row=6, column=2, sticky="ew", pady=5)
scale.grid(row=0, column=3, rowspan=6, padx=10)
secret_key.grid(row=6, column=3, rowspan=8, padx=10)

# Запускаем главный цикл событий
tick()
root.mainloop()

