import os
import netCDF4 as nc
import pandas as pd
import streamlit as st
from shapely.geometry import Point, Polygon

def extract_nc_to_dataframe(folder_path):
    """
    Извлекает данные из NetCDF файлов и форматирует их в таблицу с колонками:
    'время', 'координаты' и 'значение'. Отбираются только данные, попадающие внутрь границ Египта.
    """
    # Список для хранения всех данных
    all_data = []

    # Определяем границы Египта как полигон
    egypt_polygon = Polygon([
        (24.7, 22.0),   # Юго-запад
        (35.0, 22.0),   # Юго-восток
        (35.0, 31.5),   # Северо-восток
        (24.7, 31.5),   # Северо-запад
    ])

    # Список файлов NetCDF
    files = [f for f in os.listdir(folder_path) if f.endswith(".nc")]
    if not files:
        print("Нет файлов NetCDF в указанной папке.")
        return pd.DataFrame()

    # Обработка каждого файла
    for file in files:
        file_path = os.path.join(folder_path, file)
        dataset = nc.Dataset(file_path)

        # Проверка наличия времени, широты, долготы и значения
        time_var = dataset.variables.get('time')
        lat_var = dataset.variables.get('latitude')
        lon_var = dataset.variables.get('longitude')

        value_var = next((v for v in dataset.variables if v not in ['time', 'latitude', 'longitude']), None)

        if time_var is None or lat_var is None or lon_var is None or value_var is None:
            print(f"Пропущены обязательные переменные в файле {file}")
            continue

        # Преобразование времени в удобный формат
        time_units = getattr(time_var, "units", "seconds since 1970-01-01 00:00:00")
        time_calendar = getattr(time_var, "calendar", "gregorian")
        times = nc.num2date(time_var[:], units=time_units, calendar=time_calendar)

        # Извлечение координат
        lats = lat_var[:]
        lons = lon_var[:]
        # Преобразование долготы из [0, 360] в [-180, 180]
        lons = [(lon - 360 if lon > 180 else lon) for lon in lons]

        values = dataset.variables[value_var][:]

        # Создание таблицы
        for t_idx, time in enumerate(times):
            if values.ndim == 3:  # Данные зависят от времени
                for lat_idx, lat in enumerate(lats):
                    for lon_idx, lon in enumerate(lons):
                        if egypt_polygon.contains(Point(lon, lat)):  # Проверка попадания в границы Египта
                            all_data.append({
                                "Время": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "Координаты Египта (широта, долгота)": f"{lat:.2f}, {lon:.2f}",
                                "Радиационное воздействие аэрозолей с излучением": values[t_idx, lat_idx, lon_idx]
                            })
            elif values.ndim == 2:  # Данные зависят только от координат
                for lat_idx, lat in enumerate(lats):
                    for lon_idx, lon in enumerate(lons):
                        if egypt_polygon.contains(Point(lon, lat)):  # Проверка попадания в границы Египта
                            all_data.append({
                                "Время": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "Координаты Египта (широта, долгота)": f"{lat:.2f}, {lon:.2f}",
                                "Радиационное воздействие аэрозолей с излучением": values[lat_idx, lon_idx]
                            })
            else:
                print(f"Неизвестная структура данных в файле {file}")

        dataset.close()

    # Конвертация данных в DataFrame
    df = pd.DataFrame(all_data)
    return df

def main():
    # Путь к папке с NetCDF файлами
    folder_path = "./2003-2018"  # Укажите правильный путь к вашим файлам

    # Извлечение данных и создание таблицы
    df = extract_nc_to_dataframe(folder_path)

    if df.empty:
        st.write("Нет данных для отображения.")
    else:
        st.write(df)

if __name__ == "__main__":
    main()
