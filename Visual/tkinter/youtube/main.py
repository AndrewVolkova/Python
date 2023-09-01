# документация по customtkinter https://customtkinter.tomschimansky.com/documentation/
# pip install pytube
# pip install customtkinter

# отсюда берем элемент сепаратор или линию
from tkinter import ttk
# отсюда берем все виджеты для GUI
import customtkinter as ctk

# этим мы воспользуемся для освобождения процесса, 
# чтобы не блокировался процесс отрисовки. Запустим поток для долгой операции
import threading

# тут мы храним основные наши настройки для визуализации
from settings import *

# непосредственно библиотека для скачивания файлов с ютуба
from pytube import YouTube

import sys
import os


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=LIGHT_GRAY)
        # создание обьекта GUI customtkinter
        # и основные настройки
        # tilte окна
        self.title("Youtube")
        # размер
        self.geometry('800x200')
        # привязка слежения нажатия клавиши esc для всего окна
        self.bind('<Escape>', lambda event: self.quit())
        # запрещение изменения размеров окна
        self.resizable(False, False)

        self.iconbitmap(self.resource_path("youtube.ico"))
      
        # конфигурация сетки расположения
        # создаем сетку с 1 колнкой и 3-мя строками с разными весами
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 2), weight=10, uniform='b')
        self.rowconfigure((1), weight=1, uniform='b')

        # создаем связочные переменные
        # для поля ввода
        self.entry_var = ctk.StringVar(
            value="https://youtu.be/AqRM5_xy4Sc")
        # для лейбла, где будем указывать название скачиваемого файла
        self.title_var = ctk.StringVar(value='')
        # для определения что поменялось выбранное значение из выпадающего списка
        self.combo_selected = ctk.BooleanVar(value=False)
        # для оповещения, что данные получены
        self.data_received = ctk.BooleanVar(value=False)
        # для отрисовки прогресса скачки для обьекта progress bar
        self.loading_progress = ctk.DoubleVar(value = 0)

        # данные
        # здесь разместим информацию о доступных звуковых дорожках
        self.audio_codecs = {}
        # здесь разместим информацию о доступных звуковых дорожках, но сменим ключи и зачения местами
        # потом пригодится для поиска выбранного id tag дорожки
        self.audio_codecs_t = {}

        # слежение (tracing)
        self.data_received.trace_add('write', self.update_combobox)
        self.combo_selected.trace_add('write', self.selected_combobox)
      

        # widgets
             
        FrameWidgetsUrl(self)
        SeparatorHLine(self, 0, 1)
        self.frame_selection = FrameWidgetsOptions(self)
        self.codec_selection = self.frame_selection.codec_selection
        self.progress_bar = self.frame_selection.progress_bar
        self.loading_widget = FrameWidgetsLoading(self)

        self.mainloop()

    # функция отвечающая за обновление данных о звуковых дорожках в запрашиваемом файле
    def update_combobox(self, *args):
        if self.audio_codecs:
            self.codec_selection.configure(
                values=tuple(self.audio_codecs.values()))
            self.audio_codecs_t = {key: id for id,
                                   key in self.audio_codecs.items()}
            self.codec_selection.set(tuple(self.audio_codecs.values())[0])
            self.loading_widget.hide()
            self.frame_selection.show()
        else:
            self.frame_selection.hide()
    
    # функция, отвечающая за изменения при выборе звуковой дорожки из выпадающего списка
    def selected_combobox(self, *args):

        self.loading_progress.set(0)

        # print(k := self.codec_selection.get())
        # print(self.audio_codecs_t.get(k))

    # функция, отвечающая за показ прогресса скачивания файла
    def on_progress(self,stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        pct_completed = bytes_downloaded / total_size * 100
        # изменяем значение в связанной переменной
        self.loading_progress.set(pct_completed/100)
        
        # print(f"Status: {round(pct_completed, 2)} %")

    # Необходимо для смены путей поиска иконки для title
    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

class FrameWidgetsUrl(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=LIGHT_GRAY)
        # layout
        self.grid(row=0, column=0)
        # layout
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')
        self.rowconfigure(2, weight=1, uniform='a')
        self.columnconfigure(0, weight=4, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')

        LabelDescription(self, 'Введите url', 0, 0, 'w')
        UrlEntry(self, parent.entry_var, 0, 1, 'we', padx=(0, 40))
        ButtonConfirm(self, parent, 'Получить данные',
                      1, 1, sticky='e', padx=(10, 0))
        LabelTitle(self,parent.title_var,0,2, sticky='w', pady=(10,0))

class FrameWidgetsOptions(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=LIGHT_GRAY)
        # layout
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')
        self.rowconfigure(2, weight=1, uniform='a')
        self.columnconfigure(0, weight=4, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        
        LabelDescription(self, 'Опции файла', 0, 0, 'w', padx=0)

        self.codec_selection = CodecSelection(
            self, parent.combo_selected, 0, 1, 'we', padx=(0, 40))
        ButtonDownload(self, parent, 'Скачать', 1, 1, sticky='e', padx=(10, 0))

        self.progress_bar = ProgressBar(self, parent.loading_progress, 0, 2)
        
    def show(self):
        self.grid(row=2, column=0)

    def hide(self):
        self.grid_remove()

class FrameWidgetsLoading(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=LIGHT_GRAY)
        # layout
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')

        LabelDescription(self, 'Загружаем информацию о файле...',
                         0, 0, 'snew', padx=0, color=BLUE)

    def show(self):
        self.grid()

    def hide(self):
        self.grid_remove()

class LabelDescription(ctk.CTkLabel):
    def __init__(self, parent, text, column, row, sticky='we', padx=0, pady=(0, 3), color=BLACK):
        font = ctk.CTkFont(family=FONT, size=INPUT_FONT_SIZE, weight='bold')
        super().__init__(master=parent, text=text, font=font, text_color=color)
        self.grid(column=column, row=row, sticky=sticky, padx=padx, pady=pady)

class LabelTitle(ctk.CTkLabel):
    def __init__(self, parent, textvariable, column, row, sticky='we', padx=0, pady=(0, 3), color=BLUE):
        font = ctk.CTkFont(family=FONT, size=LABEL_FONT_SIZE, weight='bold')
        super().__init__(master=parent, textvariable = textvariable, font=font, text_color=color)
        self.grid(column=column, row=row, sticky=sticky, padx=padx, pady=pady)

class UrlEntry(ctk.CTkEntry):
    def __init__(self, parent, textvariable, column, row, sticky='we', padx=0, pady=0):
        super().__init__(master=parent, textvariable=textvariable,
                         corner_radius=BUTTON_CORNER_RADIUS, border_width=BORDER_WIDTH, border_color=DARK_GRAY)
        self.grid(column=column, row=row, sticky=sticky, padx=padx, pady=pady)

class ButtonConfirm(ctk.CTkButton):
    def __init__(self, parent, youtube, text, column, row, *, sticky='we', padx=0, pady=0):
        self.parent = youtube
        super().__init__(master=parent, text=text,
                         command=self.on_submit, corner_radius=BUTTON_CORNER_RADIUS)
        self.grid(column=column, row=row, sticky=sticky, padx=padx, pady=pady)
        
    def download_audio_streams(self, url):
        self.parent.youtube_object = YouTube(url, on_progress_callback=self.parent.on_progress)
        audio_streams = self.parent.youtube_object.streams.filter(only_audio=True)
        audio_codecs = {
            _.itag: f"{_.mime_type}:{_.abr} - {_.codecs[0]}" for _ in audio_streams}
        return audio_codecs

    def on_submit_async(self, url):
        audio_codecs = self.download_audio_streams(url)
        self.parent.audio_codecs.update(audio_codecs)
        self.parent.data_received.set(True)
        self.parent.title_var.set(self.parent.youtube_object.title)

    def on_submit(self):
        self.parent.frame_selection.hide()
        self.parent.loading_widget.show()
        url = self.parent.entry_var.get()

        thread = threading.Thread(target=self.on_submit_async, args=(url,))
        thread.start()

        thread.join(timeout=0)

class ButtonDownload(ctk.CTkButton):
    def __init__(self, parent, youtube, text, column, row, *, sticky='we', padx=0, pady=0):
        self.parent = youtube
        super().__init__(master=parent, text=text,
                         corner_radius=BUTTON_CORNER_RADIUS,
                         command=self.on_download)
        self.grid(column=column, row=row, sticky=sticky, padx=padx, pady=pady)

    def on_download_async(self, stream):
        stream.download()
        self.parent.progress_bar.hide()
        
    def on_download(self):
        selected_option = self.parent.codec_selection.get()
        id = self.parent.audio_codecs_t.get(selected_option)
       
        out = self.parent.youtube_object.streams.get_by_itag(id)
        self.parent.progress_bar.show()
        thread = threading.Thread(target=self.on_download_async, args = (out,))
        thread.start()
        
        thread.join(timeout=0)

class CodecSelection(ctk.CTkComboBox):
    def __init__(self, parent, textvariable, column, row, sticky='we', padx=0, pady=0):
        # data
        self.textvariable = textvariable
        super().__init__(master=parent,
                         state='readonly',
                         command=self.on_change,
                         corner_radius=BUTTON_CORNER_RADIUS,
                         border_width=BORDER_WIDTH,
                         border_color=DARK_GRAY,
                         )
        self.grid(column=column, row=row, sticky=sticky, padx=padx, pady=pady)

    def on_change(self, *args):
        self.textvariable.set(True)

class SeparatorHLine(ttk.Separator):
    def __init__(self, parent, column, row):
        super().__init__(master=parent, orient="horizontal")
        self.grid(column=column, row=row, sticky="ew")

class ProgressBar(ctk.CTkProgressBar):
    def __init__(self, parent, loading_progress, column, row, sticky='we', padx=0, pady=0):
        self.column = column
        self.row = row
        self.sticky = sticky
        self.padx = padx
        self.pady = pady
        
        super().__init__(master = parent, corner_radius = BUTTON_CORNER_RADIUS,
                        variable = loading_progress,
                         )
    def show(self):
        self.grid(column=self.column, row=self.row, sticky=self.sticky, padx=self.padx, pady=self.pady, columnspan=2)
    def hide(self):
        self.grid_remove()    


if __name__ == '__main__':
    App()

# компилируем
# python -m PyInstaller -F main.py --onefile --collect-all customtkinter -w
# python -m PyInstaller -F --name=youtube --onefile main.py --collect-all customtkinter -w
# --onefile - указываем что нужн один файл, т.е. exe
# --collect-all customtkinter - указываем чтобы все что относится к customtkinter, включая темы, было добавлено в exe
# -w указываем что приложение следует запустить в режиме без консоли
# --icon=<путь к иконке>, меняем на свою иконку для exe файла

# компилируем из спецификации
# python -m PyInstaller .\main.spec
# python -m PyInstaller .\youtube.spec
