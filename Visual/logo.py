# -*- coding: utf-8 -*-

import sys
from PIL import Image, ImageDraw, ImageFont

PG_LOGO = "F:/DaVinci/images/coding_sm.png"
WN_ICONS = "F:/DaVinci/images/window_icons.png"
OUTPUT_PATH = "F:/TG/questions/"

def add_logo_and_title(image_path, logo_path, title_text, output_path):
    # Открываем основное изображение
    image = Image.open(image_path)
    width, height = image.size

    # Открываем логотип и задаем его размер относительно основного изображения
    logo = Image.open(logo_path)

    # Создаем новое изображение с дополнительным местом для текста
    new_height = height + 60  # Добавляем место для заголовка
    new_image = Image.new("RGB", (width, new_height), "white")
    new_image.paste(image, (0, 60))

    # Накладываем логотип на изображение (в правый нижний угол)
    logo_x = width - logo.width - 10
    logo_y = height - logo.height - 10
    new_image.paste(logo, (logo_x, logo_y), logo if logo.mode == 'RGBA' else None)

    wn_icons = Image.open(WN_ICONS)
    new_image.paste(wn_icons, (20,18), wn_icons if wn_icons.mode == 'RGBA' else None)
    
    
    # Добавляем заголовок
    draw = ImageDraw.Draw(new_image)
    try:
        font = ImageFont.truetype("C:/Users/Andrew/AppData/Local/Microsoft/Windows/Fonts/Rubik-Regular.ttf", 36)  # Замените на путь к шрифту, если необходимо
    except IOError:
        font = ImageFont.load_default()

    title_width, title_height = draw.textbbox((0, 0), title_text, font=font)[2:]  # Определяем размеры текста с помощью textbbox
    title_x = (width - title_width) // 2
    title_y = 10  # Заголовок выше изображения
    draw.text((title_x, title_y), title_text, fill="black", font=font)

    # Сохраняем результат
    new_image.save(output_path)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) != 3:
        print("Usage: python script.py <image_path> <question_number>")
        sys.exit(1)

    image_path = sys.argv[1]
    logo_path = PG_LOGO
    question_number = sys.argv[2] 
    title_text = f'Вопрос дня: N{question_number}'

    output_path = f'{OUTPUT_PATH}question_{question_number}_pythongurutg.png'

    add_logo_and_title(image_path, logo_path, title_text, output_path)
