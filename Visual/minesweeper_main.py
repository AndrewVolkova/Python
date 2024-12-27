import pyautogui
import random
import time
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow
import threading


class OverlayWindow(QMainWindow):
    def __init__(self, game_area):
        super().__init__()

        self.game_area = game_area
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Игнорируем ввод мыши

        # Устанавливаем окно размером на весь экран
        self.setGeometry(0, 0, pyautogui.size().width, pyautogui.size().height)
        
    

    def paintEvent(self, event):
        """ Рисуем рамку вокруг области игрового поля """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QColor(0, 255, 0, 255)  # Зеленый цвет
        thickness = 15  # Толщина линии рамки
        painter.setPen(QPen(pen, thickness))
        painter.setBrush(Qt.NoBrush)  # Убираем заливку

        # Координаты рамки
        x, y, width, height = self.game_area
        painter.drawRect(x, y, width, height)

        painter.end()
        
def find_game_area(template="minesweeper.png"):
    """ 
    Найти поле Сапера на экране по шаблону.
    Вернет координаты области игры (x, y, width, height).
    """
    print("Ищем игровую область...")

    try:
        game_area = pyautogui.locateOnScreen(template,  minSearchTime=1, confidence=0.9)
        print("Поле найдено:", game_area)
        return game_area
    except:
        print("Поле не найдено. Убедитесь, что игра открыта, и шаблон корректен.")
        return None

def click_random_cell(game_area, step, cell_size=165):
    """ 
    Кликает в случайной ячейке на поле игры.
    :param game_area: Координаты области игрового поля (x, y, width, height).
    :param cell_size: Размер одной клетки в пикселях.
    """
    x_start, y_start, width, height = game_area

    # Генерация координат случайной ячейки
    rand_x = x_start + random.randint(0, width // cell_size - 1) * cell_size + cell_size // 2
    rand_y = y_start + random.randint(0, height // cell_size - 1) * cell_size + cell_size // 2

    pyautogui.click(rand_x, rand_y)
    
    print(f"{step}: Кликнул в клетку: ({rand_x}, {rand_y})")

def detect_game_over(game_over_template="minesweeper_game_over.png", new_game_button="new_game_button.png"):
    """
    Проверяет, завершена ли игра, и нажимает на кнопку «New Game», если шаблон найден.
    :param game_over_template: Путь к изображению, определяющему конец игры.
    :param new_game_button: Путь к изображению кнопки новой игры.
    """
    print("Проверяем конец игры...")
    try:
        game_over = pyautogui.locateOnScreen(game_over_template, confidence=0.4)
    except:
        game_over = None    
    
    if game_over:
        print("Конец игры обнаружен!")
        # Попытка нажать на кнопку новой игры
        new_game = pyautogui.locateOnScreen(new_game_button, confidence=0.5)
        if new_game:
            pyautogui.click(new_game)
            print("Нажата кнопка «New Game».")
            time.sleep(2)  # Задержка перед началом новой игры
        else:
            print("Кнопка «New Game» не найдена.")
        return True
    
    return False

def game_loop(game_area, app, max_moves=4):
    """ Игровой цикл """
    for _ in range(max_moves):
        # Проверить завершение игры
        if detect_game_over():
            print("Пробуем начать следующую игру")
            continue

        click_random_cell(game_area, _)
        time.sleep(1)  # Пауза для обновления экрана

    app.quit()

def main():
    # Найти игровую область
    game_area = find_game_area()
    if not game_area:
        return
    
    # Запуск GUI
    app = QApplication([])
    overlay = OverlayWindow(game_area)

    # Игровой цикл в отдельном потоке
    game_thread = threading.Thread(target=game_loop, args=(game_area, app))
    game_thread.daemon = True  # Поток завершится, если основной поток завершится
    game_thread.start()

    # Отобразить рамку поверх экрана
    overlay.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


# https://www.msn.com/en-us/play/games/microsoft-minesweeper/cg-msminesweeper?ocid=cganswer&cgfrom=cg_ans_game_play