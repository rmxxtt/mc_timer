import socket
import tkinter as tk
import tkinter.ttk as ttk
import threading
import http.client
import datetime
import math
import json
import time
import platform
import webbrowser

# Звуковое оповещение, доступно только под Windows
WINSOUND = False
if platform.system() == "Windows":
    import winsound

    WINSOUND = True

SERVER = {
    "Atlantida": 30,
    "Clans": 8,
    "Demo": 3,
    "Dragon nest": 29,
    "Farm": 22,
    "Guest": 2,
    "Hunter": 5,
    "Laboratory": 26,
    "Little big": 6,
    "Main": 1,
    "Miner": 7,
    "Monkey": 10,
    "Nano": 12,
    "Newbie": 14,
    "Novice": 19,
    "Pacific": 16,
    "Pirate station": 11,
    "Prometeus": 25,
    "Rookie": 13,
    "Team": 20,
    "Zeus": 28
}


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Скрываем окно, чтобы избежать рендера в открытом окне
        self.master.withdraw()

        self.master.title("Игровое время")
        self.master.resizable(False, False)
        self.master.iconbitmap(True, "./mcgl.ico")

        # Выбор сервера
        get_server_label = ttk.Label(text="Сервер")
        self.get_server_combobox = ttk.Combobox(values=list(SERVER.keys()), height=10,
                                                state="readonly", width=26, justify='c')
        self.get_server_combobox.current(0)
        self.get_server_thred_id = 0
        self.get_server_update_button = ttk.Button(text="Обновить", command=lambda: self.get_server())

        # Канвас: Включить, выключить анимацию
        self.canvas_animate_var = tk.BooleanVar()
        self.canvas_animate_var.set(1)
        canvas_animate_checkbutton = ttk.Checkbutton(text="Включить анимацию",
                                                     variable=self.canvas_animate_var, onvalue=1, offvalue=0)

        # <<< Место для Канваса

        sep = ttk.Separator(orient="horizontal")

        # Таймер: Включить, выключить
        self.timer_thred_id = 0
        self.timer_start_button = ttk.Button(text="Запустить таймер", command=lambda: self.timer_start())
        self.timer_stop_button = ttk.Button(text="Отключить", command=lambda: self.timer_reset_thread_id())

        # Таймер: Фрейм для информации
        timer_labelframe = ttk.LabelFrame(text="До окончания", labelanchor="n")

        # Таймер: Информация во фрейме
        timer_info_label_number_days_or_nights = ttk.Label(timer_labelframe, text="Осталось")
        timer_info_label_time_left = ttk.Label(timer_labelframe, text="Время")
        timer_info_label_server_name = ttk.Label(timer_labelframe, text="Сервер")
        self.timer_info_number_days_or_nights = ttk.Label(timer_labelframe, text="")
        self.timer_info_time_left = ttk.Label(timer_labelframe, text="")
        self.timer_info_server_name = ttk.Label(timer_labelframe, text="")

        # Таймер: настройки, Время суток
        timer_time_label = ttk.Label(text="Время суток")
        self.timer_time_var = tk.IntVar()
        self.timer_time_var.set(1)
        timer_time_frame = ttk.Frame()
        self.timer_time_day_radiobutton = ttk.Radiobutton(timer_time_frame, text='День',
                                                          variable=self.timer_time_var, value=1)
        self.timer_time_night_radiobutton = ttk.Radiobutton(timer_time_frame, text='Ночь',
                                                            variable=self.timer_time_var, value=0)

        # Таймер: настройки, Событие
        timer_event_label = ttk.Label(text="Событие")
        self.timer_event_var = tk.IntVar()
        self.timer_event_var.set(1)
        timer_event_frame = ttk.Frame()
        self.timer_event_start_radiobutton = ttk.Radiobutton(timer_event_frame, text='Начало',
                                                             variable=self.timer_event_var, value=1)
        self.timer_event_end_radiobutton = ttk.Radiobutton(timer_event_frame, text='Конец',
                                                           variable=self.timer_event_var, value=0)

        # Таймер: настройки, Очередь
        timer_queue_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        timer_queue_label = ttk.Label(text="Очередь")
        self.timer_queue_combobox = ttk.Combobox(values=timer_queue_list, state="readonly", justify="c")
        self.timer_queue_combobox.current(0)

        # Таймер: настройки, Учитывать текущее время суток
        self.timer_current_time_var = tk.BooleanVar()
        self.timer_current_time_var.set(1)
        self.timer_current_time_checkbutton = ttk.Checkbutton(text="Учитывать текущее время суток",
                                                              variable=self.timer_current_time_var, onvalue=1,
                                                              offvalue=0)

        # Таймер: настройки, Звук
        self.timer_sound_alert_var = tk.BooleanVar()
        timer_sound_alert_checkbutton = ttk.Checkbutton(text="Включить звуковое оповещение",
                                                        variable=self.timer_sound_alert_var, onvalue=1, offvalue=0)
        # Настройка звука доступна только на Windows
        if WINSOUND:
            self.timer_sound_alert_var.set(1)
        else:
            self.timer_sound_alert_var.set(0)
            timer_sound_alert_checkbutton.config(state="disabled")

        # О программе
        about_button = ttk.Button(text="О программе", command=lambda: self.about())

        # Настройки сетки
        get_server_label.grid(row=0, column=0, sticky="w", pady=10, padx=10)
        self.get_server_combobox.grid(row=0, column=1, padx=10, sticky="we")
        self.get_server_update_button.grid(row=1, column=0, padx=10, pady=10, ipadx=10, ipady=10, sticky="wen")
        canvas_animate_checkbutton.grid(row=2, column=0, padx=10, pady=10, sticky="s")
        # <<< Место для Канваса
        sep.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.timer_start_button.grid(row=4, column=0, columnspan=1, padx=10, pady=(10, 5),
                                     ipadx=10, ipady=10, sticky="we")
        self.timer_stop_button.grid(row=5, column=0, columnspan=1, padx=10, pady=(5, 10),
                                    ipadx=10, ipady=10, sticky="we")
        # Фрейм
        timer_labelframe.grid(row=4, column=1, rowspan=2, pady=10, padx=10, sticky="snwe")
        timer_info_label_number_days_or_nights.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="e")
        timer_info_label_time_left.grid(row=1, column=0, columnspan=1, pady=(0, 0), padx=10, sticky="e")
        timer_info_label_server_name.grid(row=2, column=0, columnspan=1, pady=(0, 10), padx=10, sticky="e")
        self.timer_info_number_days_or_nights.grid(row=0, column=1, columnspan=1, pady=(10, 0), padx=10, sticky="w")
        self.timer_info_time_left.grid(row=1, column=1, columnspan=1, pady=(0, 0), padx=10, sticky="w")
        self.timer_info_server_name.grid(row=2, column=1, columnspan=1, pady=(0, 10), padx=10, sticky="w")
        # Конец фрейма
        timer_time_label.grid(row=9, column=0, pady=10, padx=10, sticky="wn")
        # Фрейм
        timer_time_frame.grid(row=9, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        self.timer_time_day_radiobutton.grid(row=0, column=0, sticky="w")
        self.timer_time_night_radiobutton.grid(row=1, column=0, sticky="w")
        # Конец фрейма
        timer_event_label.grid(row=10, column=0, pady=10, padx=10, sticky="wn")
        # Фрейм
        timer_event_frame.grid(row=10, column=1, columnspan=2, padx=10, pady=10, sticky="we")
        self.timer_event_start_radiobutton.grid(row=0, column=0, sticky="w")
        self.timer_event_end_radiobutton.grid(row=1, column=0, sticky="w")
        # Конец фрейма
        timer_queue_label.grid(row=11, column=0, pady=10, padx=10, sticky="w")
        self.timer_queue_combobox.grid(row=11, column=1, padx=10, sticky="we")
        self.timer_current_time_checkbutton.grid(row=12, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
        timer_sound_alert_checkbutton.grid(row=13, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")
        about_button.grid(row=14, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        # Канвас
        # Размер канваса зависит от размеров других виджетов, для получения которых требуется обновление
        self.master.update()
        self.canvas_height = (canvas_animate_checkbutton.winfo_height() +
                              self.get_server_update_button.winfo_height() + 20)
        self.canvas_width = self.get_server_combobox.winfo_width()
        self.canvas = tk.Canvas(height=self.canvas_height, width=self.canvas_width, bg="#f0de79")
        self.canvas.grid(row=1, column=1, rowspan=2, padx=10, pady=10)

        # Показываем готовое окно
        self.master.deiconify()

    def get_server(self):
        self.get_server_update_button.config(state="disabled")
        self.get_server_thred_id += 1
        threading.Thread(target=self.canvas_animate, args=(self.get_server_thred_id,), daemon=True).start()

    def canvas_animate(self, thred_id):
        self.canvas.delete("all")
        api = self.api_request()
        self.get_server_update_button.config(state="normal")
        if api is None:
            return
        ticks = api["time"]
        ticks %= 24000  # Текущее время в тиках

        # Синий прямоугольник - ночь, 1/2 канваса, вращается относительно точки center на фоне желтого канваса
        rectangle_night_vertex = [
            (0 - 60, 0 - 60),
            (self.canvas_width + 60, 0 - 60),
            (self.canvas_width + 60, self.canvas_height / 2 + 2),
            (0 - 60, self.canvas_height / 2 + 2)
        ]
        rectangle_night = self.canvas.create_polygon(rectangle_night_vertex, fill='#3c548c')
        center = (self.canvas_width / 2, self.canvas_height / 2 + 2)  # Поворот относительно точки

        # Верхний прямоугольник, 1/2 канваса - меняет цвет, день или ночь
        rectangle_current_vertex = [
            (0, 0),
            (self.canvas_width + 30, 0),
            (self.canvas_width + 30, self.canvas_height / 2 + 2),
            (0, self.canvas_height / 2 + 2)
        ]
        # Желтый цвет под фон канваса
        rectangle_current = self.canvas.create_polygon(rectangle_current_vertex, fill='#f0de79')

        new_rectangle_night_vertex = []

        while True:
            if thred_id != self.get_server_thred_id:
                return

            if not self.canvas_animate_var.get():
                time.sleep(1)
                ticks += 20
                if ticks > 24000:
                    ticks -= 24000
                continue

            angle = ticks * 0.015  # 1 тик = 0.015 градусов, 360 / 24000
            angle = angle * math.pi / 180.0
            for x, y in rectangle_night_vertex:  # Вращаем прямоугольник
                cos, sin = math.cos(angle), math.sin(angle)
                center_x, center_y = center
                x -= center_x
                y -= center_y
                x, y = x * cos - y * sin, y * cos + x * sin
                new_rectangle_night_vertex.extend([x + center_x, y + center_y])

            # 0 - 12000 день, 12000 - 24000 ночь, меняем цвет
            if ticks < 12000:
                self.canvas.itemconfig(rectangle_current, fill='#f0de79')
            else:
                self.canvas.itemconfig(rectangle_current, fill='#3c548c')

            # Устанавливаем новые координаты прямоугольнику
            self.canvas.coords(rectangle_night, *new_rectangle_night_vertex)
            new_rectangle_night_vertex.clear()
            time.sleep(1)
            ticks += 20
            if ticks > 24000:
                ticks -= 24000

    def api_request(self):
        # Время запроса
        time_start = time.time()
        url = "forum.minecraft-galaxy.ru"
        server_id = SERVER[self.get_server_combobox.get()]
        path = "/api/" + str(server_id) + "/serverinfo"
        server_name = None
        for key, value in SERVER.items():
            if server_id == value:
                server_name = key
        connect = http.client.HTTPConnection(url, timeout=5)
        connect.request("GET", path)
        try:
            result = connect.getresponse()
            data = json.loads(result.read())
            server_time = int(data["time"])
        except socket.timeout as error:
            self.alert("Ошибка", "Время ожидания превышено.", error)
            return None
        except ConnectionError as error:
            self.alert("Ошибка", "Сервер не отвечает. Попробуйте позже.", error)
            return None
        except (json.JSONDecodeError, KeyError, ValueError) as error:
            self.alert("Ошибка", "Получены неверные данные.", error)
            return None
        # За каждую секунду ожидания ответа добавляем 20 тиков
        if (delay := int(time.time() - time_start) / 1) > 0:
            server_time += delay * 20
        return dict(time=server_time, server=server_name)

    def alert(self, title, message, error=None):
        if self.timer_sound_alert_var.get():
            if error:
                winsound.PlaySound("SystemHand", winsound.SND_ASYNC)
            else:
                winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
        alert = tk.Toplevel(self.master)
        alert.withdraw()
        alert.resizable(False, False)
        alert.title(title)
        alert.grab_set()  # Модальное окно
        msg = ttk.Label(alert, text=message, anchor="center")
        msg.grid(padx=20, pady=20, sticky="we")
        if error:
            err = ttk.Label(alert, text=f"{error}", anchor="center")
            err.grid(padx=20, pady=(0, 20), sticky="we")
        quit_ = ttk.Button(alert, text="Закрыть окно", width=40, command=lambda: alert.destroy())
        quit_.grid(padx=10, pady=10, ipadx=10, ipady=10, sticky="we")
        alert.deiconify()

    def timer_start(self):
        self.timer_gui_state_off()
        self.timer_thred_id += 1
        threading.Thread(target=self.timer, args=(self.timer_thred_id,), daemon=True).start()

    def timer_reset_thread_id(self):
        self.timer_thred_id = 0

    def timer_stop(self):
        self.timer_reset_thread_id()
        self.timer_gui_state_on()

    def timer_gui_state_on(self):
        self.timer_start_button.config(state="normal")
        self.timer_time_day_radiobutton.config(state="normal")
        self.timer_time_night_radiobutton.config(state="normal")
        self.timer_event_start_radiobutton.config(state="normal")
        self.timer_event_end_radiobutton.config(state="normal")
        self.timer_queue_combobox.config(state="readonly")
        self.timer_current_time_checkbutton.config(state="normal")
        # Очищаем поля
        self.timer_info_number_days_or_nights.config(text="")
        self.timer_info_time_left.config(text="")
        self.timer_info_server_name.config(text="")

    def timer_gui_state_off(self):
        self.timer_start_button.config(state="disabled")
        self.timer_time_day_radiobutton.config(state="disabled")
        self.timer_time_night_radiobutton.config(state="disabled")
        self.timer_event_start_radiobutton.config(state="disabled")
        self.timer_event_end_radiobutton.config(state="disabled")
        self.timer_queue_combobox.config(state="disabled")
        self.timer_current_time_checkbutton.config(state="disabled")

    def timer(self, thred_id):
        api = self.api_request()
        if api is None:
            self.timer_stop()
            return
        ticks = api["time"]
        ticks %= 24000
        server_name = api["server"]
        self.timer_info_server_name.config(text=server_name)

        # Настройки виджетов таймера
        timer_day = self.timer_time_var.get()
        timer_night = not timer_day
        timer_event_start = self.timer_event_var.get()
        timer_event_end = not timer_event_start
        timer_use_current_time = True if self.timer_current_time_var.get() else False
        timer_queue = int(self.timer_queue_combobox.get())

        # Текущее время суток
        current_time_of_day_str = "day" if ticks < 12000 else "night"

        # Вычисляет настройки таймера
        timer_settings = self.calculate_timer_settings(
            current_time_of_day_str,
            timer_day,
            timer_night,
            timer_event_start,
            timer_event_end,
            timer_use_current_time,
            timer_queue,
            ticks
        )

        # Количество необходимых событий(начало или конец) дня или ночи для завершения таймера
        number_events = timer_settings[0]
        # Переменные для подсчета событий
        days_started = 0
        days_ended = 0
        nights_started = 0
        nights_ended = 0

        # Количество дней или ночей до завершения таймера
        countdown_days_or_nights = timer_settings[1]
        # Тип события для обратного отсчета дней или ночей
        countdown_event = timer_settings[2]

        # Количество тиков до окончания таймера
        ticks_number = timer_settings[3]

        if timer_day:
            name_time_of_days = ["день", "дня", "дней"]
        else:
            name_time_of_days = ["ночь", "ночи", "ночей"]

        while True:
            if thred_id != self.timer_thred_id:
                self.timer_stop()
                return

            # Выбор нужного склонения
            if countdown_days_or_nights == 1:
                declension = name_time_of_days[0]
            elif 2 <= countdown_days_or_nights <= 4:
                declension = name_time_of_days[1]
            else:
                declension = name_time_of_days[2]
            self.timer_info_number_days_or_nights.config(text=f"{countdown_days_or_nights} {declension}")

            # Переводим тики в секунды
            time_left = ticks_number // 20
            self.timer_info_time_left.config(text=datetime.timedelta(seconds=time_left))
            ticks_number -= 20

            # Текущее время суток до паузы
            first_time = "day" if ticks < 12000 else "night"

            time.sleep(1)
            ticks += 20
            if ticks > 24000:
                ticks -= 24000

            # Время после паузы
            next_time = "day" if ticks < 12000 else "night"

            # Сравниваем время до паузы и после, что определяет тип
            # события(начало или конец) дня и ночи и их количество
            if first_time == "day" and next_time == "night":
                days_ended += 1
                nights_started += 1
                # Проверяем, соответствует ли тип события для обратного отсчета дней или ночей
                if countdown_event == "dn":
                    countdown_days_or_nights -= 1
            elif first_time == "night" and next_time == "day":
                days_started += 1
                nights_ended += 1
                if countdown_event == "nd":
                    countdown_days_or_nights -= 1

            # Проверяем настройки таймера, далее сравниваем,
            # соотвествует ли количество событий(начало или конец) дня или ночи установленному значению
            if timer_day:
                if timer_event_start:
                    if days_started == number_events:
                        self.alert("Таймер", "Начало дня. Время действовать!")
                        self.timer_stop()
                        return
                elif timer_event_end:
                    if days_ended == number_events:
                        self.alert("Таймер", "Конец дня. Время действовать!")
                        self.timer_stop()
                        return
            elif timer_night:
                if timer_event_start:
                    if nights_started == number_events:
                        self.alert("Таймер", "Начало ночи. Время действовать!")
                        self.timer_stop()
                        return
                elif timer_event_end:
                    if nights_ended == number_events:
                        self.alert("Таймер", "Конец ночи. Время действовать!")
                        self.timer_stop()
                        return

    @staticmethod
    def calculate_timer_settings(current_time_of_day_str, timer_day, timer_night, timer_event_start,
                                 timer_event_end, timer_use_current_time, timer_queue, ticks):

        # Количество необходимых событий(начало или конец) дня или ночи для завершения таймера
        number_events = None

        # Количество дней или ночей до завершения таймера
        countdown_days_or_nights = None
        # Тип события для обратного отсчета дней или ночей
        countdown_event = None

        # Количество тиков до окончания таймера
        ticks_number = None

        # Вернет общее количество дней и ночей до окончания таймера, не учитывает текущее время суток
        #
        # Настройки таймера имеют 16 вариантов. Искомый ключ(target_key) является порядковым номером
        # в очереди(timer_queue). Первый ключ любого варианта(init_key) - это первый элемент очереди, значение
        # которого(init_value) - это количество дней и ночей до окончания таймера, не учитывая текущее время суток.
        # Арифметическая прогрессия с шагом(step_value). Находим значение искомого ключа - общее количество
        # дней и ночей до окончания таймера, не учитывая текущее время суток.
        def found_key_value(init_key, init_value, step_value, target_key):
            number_days_and_nights = (target_key - init_key) * step_value + init_value
            return number_days_and_nights

        # Вернет количество тиков до окончания таймера
        def get_ticks_number(number_days_and_nights):
            if current_time_of_day_str == "day":
                ticks_left = 12000 - ticks
            else:
                ticks_left = 24000 - ticks
            return 12000 * number_days_and_nights + ticks_left

        # Все 16 вариантов
        if current_time_of_day_str == "day":
            if timer_day:
                if timer_event_start and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
                elif timer_event_end and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 0, 2, timer_queue))
                elif timer_event_start and not timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
                elif timer_event_end and not timer_use_current_time:
                    number_events = timer_queue + 1
                    countdown_days_or_nights = timer_queue + 1
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 2, 2, timer_queue))
            elif timer_night:
                if timer_event_start and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue - 1
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 0, 2, timer_queue))
                elif timer_event_end and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
                elif timer_event_start and not timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue - 1
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 0, 2, timer_queue))
                elif timer_event_end and not timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
        elif current_time_of_day_str == "night":
            if timer_day:
                if timer_event_start and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue - 1
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 0, 2, timer_queue))
                elif timer_event_end and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
                elif timer_event_start and not timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue - 1
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 0, 2, timer_queue))
                elif timer_event_end and not timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "dn"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
            elif timer_night:
                if timer_event_start and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
                elif timer_event_end and timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 0, 2, timer_queue))
                elif timer_event_start and not timer_use_current_time:
                    number_events = timer_queue
                    countdown_days_or_nights = timer_queue
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 1, 2, timer_queue))
                elif timer_event_end and not timer_use_current_time:
                    number_events = timer_queue + 1
                    countdown_days_or_nights = timer_queue + 1
                    countdown_event = "nd"
                    ticks_number = get_ticks_number(found_key_value(1, 2, 2, timer_queue))

        return number_events, countdown_days_or_nights, countdown_event, ticks_number

    @staticmethod
    def open_url(url):
        threading.Thread(target=webbrowser.open_new, args=(url,), daemon=True).start()

    def about(self):
        about = tk.Toplevel(self.master)
        about.withdraw()
        about.resizable(False, False)
        about.title("О программе")
        about.grab_set()
        text = tk.Text(about, height=25, width=50, wrap=tk.WORD, padx=25, pady=10)
        text.grid(row=0, columnspan=2, padx=10, pady=10, ipadx=10, ipady=10)
        text.insert(tk.INSERT, ABOUT)
        text.config(state="disabled")
        scroll_bar = tk.Scrollbar(about, command=text.yview, orient="vertical")
        scroll_bar.grid(row=0, column=1, sticky="nse", padx=10, pady=10,)
        text.configure(yscrollcommand=scroll_bar.set)
        forum_url = "https://forum.minecraft-galaxy.ru"
        community_url = "https://forum.minecraft-galaxy.ru/hforum/3450"
        open_forum = ttk.Button(about, text="На сайт", command=lambda: self.open_url(forum_url))
        open_community = ttk.Button(about, text="В группу", command=lambda: self.open_url(community_url))
        open_forum.grid(row=1, column=0, padx=10, pady=10, ipady=5, sticky="we")
        open_community.grid(row=1, column=1, padx=10, pady=10, ipady=5, sticky="we")
        about.deiconify()


ABOUT = """
Программа позволяет узнать время суток, сколько осталось до завершения дня или ночи и запустить таймер.

Как узнать игровое время?
- Выбрать нужный сервер и нажать "Обновить"

Анимация смены дня и ночи
- Верхняя половина окна(прямоугольник) - показывает текущее время суток на сервере. День - желтый цвет, ночь - синий.
- В нижней части можно заметить, как день и ночь сменяют друг друга, показывая сколько осталось до завершения. \
Как только один из цветов закроет всю нижнюю половину, наступит день или ночь в зависимости от цвета. \
Вращение по часовой.

Можно ли обновлять игровое время при работающем таймере?
- Можно, как и в обратную сторону. Таймер и игровое время работают отдельно друг от друга

Как работает таймер?
-Таймер устанавливается на определенное событие дня или ночи. Это начало дня, конец дня, начало ночи и конец ночи. \
Очередь указывает какое по счету событие вас интересует.

Что значит Учитывать текущее время суток?
- Учитывать текущий день или ночь. Например на сервере сейчас день, и вы установили таймер \
на конец первого дня и настройка включена. Это значит, что таймер сработает в конце текущего дня. Если настройку \
выключить, текущий день не будет учтен. Это значит, что закончится текущий день, далее пройдет ночь, и лишь на \
конец слудующего дня сработает таймер.

Специально для minecraft-galaxy.ru
"""


if __name__ == '__main__':
    def main():
        master = tk.Tk()
        app = App(master)
        app.mainloop()


    main()
