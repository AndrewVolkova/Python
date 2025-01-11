import json
import asyncio
import os
import re
from tqdm import tqdm

# Загрузка ссылок из файла
with open("golyak_series.json", "r", encoding="utf-8") as json_file:
    links = json.load(json_file)

# Функция загрузки и конвертации одного файла
async def download_and_convert(url, output_path, position, progress_bars):
    """
    Загрузка и конвертация одного файла с использованием asyncio.
    """
    tqdm.write(f"Запускаем загрузку и конвертацию для {output_path} из {url}")

    log_file = f"{output_path}.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    command = [
        'ffmpeg',
        '-i', url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        output_path,
        '-progress', log_file,
        '-nostats',
    ]

    process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    total_duration = None
    progress_update_threshold = 0.5

    progress_bar = tqdm(
        total=0, desc=f"Загрузка {output_path}",
        position=position, ncols=100, unit="с", leave=False
    )
    progress_bars[position] = progress_bar

    try:
        async for line in process.stderr:
            line = line.decode('utf-8')
            if "Duration" in line:
                match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", line)
                if match:
                    hours, minutes, seconds = map(float, match.groups())
                    total_duration = hours * 3600 + minutes * 60 + seconds
                    tqdm.write(f"Длительность видео {url}: {total_duration} секунд.")
                    progress_bar.total = total_duration
                    break

        if total_duration is None:
            tqdm.write(f"Не удалось извлечь длительность для {url}. Пропускаем файл.")
            return

        previous_time = 0
        while True:
            if process.returncode is not None:
                if process.returncode == 0:
                    tqdm.write(f"Успешная загрузка {output_path}.")
                else:
                    tqdm.write(f"Ошибка при загрузке {output_path}. Код возврата: {process.returncode}")
                break

            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    if "out_time=" in line:
                        match = re.search(r"out_time=(\d+:\d+:\d+\.\d+)", line)
                        if match:
                            time_str = match.group(1)
                            hours, minutes, seconds = map(float, time_str.split(":"))
                            current_time = hours * 3600 + minutes * 60 + seconds
                            if current_time - previous_time >= progress_update_threshold:
                                progress_bar.n = round(current_time,2)
                                progress_bar.set_postfix({'time': f"{current_time:.2f}/{total_duration:.2f}"})
                                progress_bar.update(0)
                                previous_time = current_time
            await asyncio.sleep(0.5)

    finally:
        progress_bar.close()
        del progress_bars[position]  # Удаляем прогресс-бар после завершения
        if process.returncode is None:
            process.terminate()
        await process.wait()

# Функция параллельной загрузки файлов
async def download_all_parallel(links, max_workers=6):
    """
    Параллельная загрузка всех файлов с ограничением потоков.
    """
    tasks = []
    semaphore = asyncio.Semaphore(max_workers)
    progress_bars = {}

    tqdm.write("Запуск загрузки файлов...")

    async def download_file(semaphore, url, output_path, position, progress_bars):
        async with semaphore:
            try:
                await download_and_convert(url, output_path, position, progress_bars)
            except Exception as e:
                tqdm.write(f"Ошибка при обработке {output_path}: {str(e)}")

    position = 0
    for season, episodes in links.items():
        for episode, url in episodes.items():
            output_path = f"s{season}e{episode}.mp4"
            tasks.append(download_file(semaphore, url, output_path, position, progress_bars))
            position += 1

    await asyncio.gather(*tasks, return_exceptions=True)

# Главная функция
def main():
    try:
        asyncio.run(download_all_parallel(links, max_workers=6))
    except RuntimeError as e:
        tqdm.write(f"RuntimeError: {str(e)}")

# Запуск скрипта
if __name__ == "__main__":
    main()
