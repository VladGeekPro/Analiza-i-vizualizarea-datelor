import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_statistics(df, column_name):
    """Вычисляет базовые статистические показатели."""
    stats = df[column_name].describe()
    stats["median"] = df[column_name].median()
    stats["std"] = df[column_name].std()
    return stats

def analyze_time_series(df, column_name, pollutant_name):
    """График временных рядов для выбранного загрязнителя."""
    time_series = df.groupby("Время")[column_name].mean()

    st.subheader(f"Тенденция {pollutant_name} во времени")
    fig, ax = plt.subplots()
    time_series.plot(ax=ax, ylabel=f"{pollutant_name}", xlabel="Время")
    st.pyplot(fig)

def heatmap_pollution(df, column_name, pollutant_name):
    """Тепловая карта концентраций поллютантов."""
    st.subheader(f"Тепловая карта уровней {pollutant_name}")

    # Создание сводной таблицы для тепловой карты
    heatmap_data = df.pivot_table(index="Широта", columns="Долгота", values=column_name, aggfunc="mean")

    # Построение тепловой карты
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="viridis", cbar_kws={"label": f"Уровень {pollutant_name}"}, ax=ax)
    ax.invert_yaxis()  # Инверсия оси Y для правильного географического отображения
    ax.set_xlabel("Долгота")
    ax.set_ylabel("Широта")
    st.pyplot(fig)

def bar_chart_pollutants(df, column_name, pollutant_name):
    """Диаграмма баров для сравнения уровней поллютантов."""
    st.subheader(f"Сравнение уровней {pollutant_name} между регионами")

    # Группировка по регионам
    region_stats = df.groupby(["Широта", "Долгота"])[column_name].mean().reset_index()

    # Построение диаграммы баров
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(data=region_stats, x="Долгота", y=column_name, hue="Широта", palette="viridis", dodge=False)
    plt.xticks(rotation=90)
    ax.set_xlabel("Долгота")
    ax.set_ylabel(f"Уровень {pollutant_name}")
    st.pyplot(fig)

def get_coordinate_column(df):
    """Определяет название колонки с координатами."""
    for col in df.columns:
        if "Координаты" in col and "(широта, долгота)" in col:
            return col
    return None

def filter_data_by_date_and_coords(df, start_date, end_date, min_lat, max_lat, min_lon, max_lon):
    """Фильтрует данные по диапазону дат и координат."""
    # Приведение дат из Streamlit к типу datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Фильтр по дате
    df = df[(df["Время"] >= start_date) & (df["Время"] <= end_date)]
    # Фильтр по координатам
    df = df[(df["Широта"] >= min_lat) & (df["Широта"] <= max_lat) &
            (df["Долгота"] >= min_lon) & (df["Долгота"] <= max_lon)]
    return df

def main():
    # Пути к файлам
    file_paths = {
        "Egypt": {
            "file": "MergedTableEgyptAerosolMethaneDioxideCarbon_2003_2018.csv",
            "name": "Египте"
        },
        "Sudan": {
            "file": "MergedTableSudanAerosolDioxideCarbonMethane_2003_2018.csv",
            "name": "Судане"
        }
    }

    # Пользовательский выбор страны
    country = st.sidebar.selectbox("Выберите страну", list(file_paths.keys()))

    # Получение информации о выбранной стране
    selected_country = file_paths[country]
    selected_file = selected_country["file"]
    country_name = selected_country["name"]

    # Заголовок
    st.title(f"Анализ уровня поллютантов в {country_name} (2003-2018)")

    try:
        # Загрузка выбранной таблицы
        df = pd.read_csv(selected_file, index_col=0)
        df["Время"] = pd.to_datetime(df["Время"])

        # Определение колонки с координатами
        coordinate_column = get_coordinate_column(df)
        if not coordinate_column:
            st.error("Ошибка: Колонка с координатами не найдена!")
            return

        # Разделение широты и долготы
        df["Широта"] = df[coordinate_column].apply(lambda x: float(x.split(",")[0]))
        df["Долгота"] = df[coordinate_column].apply(lambda x: float(x.split(",")[1]))

        st.dataframe(df)

        # Выбор поллютанта
        pollutants = [col for col in df.columns if "Радиационное воздействие" in col or "Диоксид углерода" in col]
        selected_pollutant = st.sidebar.selectbox("Выберите поллютант для анализа", pollutants)

        # Выбор диапазона дат
        min_date, max_date = df["Время"].min(), df["Время"].max()
        start_date = st.sidebar.date_input("Начальная дата", value=min_date.date(), min_value=min_date.date(), max_value=max_date.date())
        end_date = st.sidebar.date_input("Конечная дата", value=max_date.date(), min_value=min_date.date(), max_value=max_date.date())

        # Выбор координат
        min_lat, max_lat = df["Широта"].min(), df["Широта"].max()
        min_lon, max_lon = df["Долгота"].min(), df["Долгота"].max()
        selected_min_lat = st.sidebar.slider("Минимальная широта", float(min_lat), float(max_lat), float(min_lat))
        selected_max_lat = st.sidebar.slider("Максимальная широта", float(min_lat), float(max_lat), float(max_lat))
        selected_min_lon = st.sidebar.slider("Минимальная долгота", float(min_lon), float(max_lon), float(min_lon))
        selected_max_lon = st.sidebar.slider("Максимальная долгота", float(min_lon), float(max_lon), float(max_lon))

        # Фильтрация данных
        filtered_df = filter_data_by_date_and_coords(df, start_date, end_date, selected_min_lat, selected_max_lat, selected_min_lon, selected_max_lon)

        # Статистические показатели
        st.header(f"1. Базовая статистика для {selected_pollutant}")
        stats = calculate_statistics(filtered_df, selected_pollutant)
        st.write(stats)

        # Анализ временных рядов
        st.header(f"2. График временных рядов для {selected_pollutant}")
        analyze_time_series(filtered_df, selected_pollutant, selected_pollutant)

        # Тепловая карта
        st.header(f"3. Тепловая карта концентраций {selected_pollutant}")
        heatmap_pollution(filtered_df, selected_pollutant, selected_pollutant)

        # Диаграмма баров
        st.header(f"4. Сравнение уровней {selected_pollutant} между регионами")
        bar_chart_pollutants(filtered_df, selected_pollutant, selected_pollutant)

    except Exception as e:
        st.error(f"Ошибка при обработке данных: {e}")

if __name__ == "__main__":
    main()
