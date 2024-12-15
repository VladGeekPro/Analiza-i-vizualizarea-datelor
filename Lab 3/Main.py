import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def calculate_statistics(df):
    """Вычисляет базовые статистические показатели."""
    stats = df["Радиационное воздействие метана (Вт/м²)"].describe()
    stats["median"] = df["Радиационное воздействие метана (Вт/м²)"].median()
    stats["std"] = df["Радиационное воздействие метана (Вт/м²)"].std()
    return stats


def analyze_time_series(df):
    """Анализ временных рядов для выбранного уровня загрязнения."""
    df["Время"] = pd.to_datetime(df["Время"])
    time_series = df.groupby("Время")["Радиационное воздействие метана (Вт/м²)"].mean()

    # Построение графика
    st.subheader("График временных рядов")
    fig, ax = plt.subplots()
    time_series.plot(ax=ax, title="Тенденция уровня метана во времени", ylabel="Уровень метана (Вт/м²)", xlabel="Время")
    st.pyplot(fig)


def heatmap_pollution(df):
    """Создание тепловой карты для визуализации концентраций метана."""
    st.subheader("Тепловая карта концентрации метана")
    df["Широта"] = df["Координаты Египта (широта, долгота)"].apply(lambda x: float(x.split(",")[0]))
    df["Долгота"] = df["Координаты Египта (широта, долгота)"].apply(lambda x: float(x.split(",")[1]))

    # Сортировка данных по широте и долготе
    df = df.sort_values(by=["Широта", "Долгота"], ascending=[True, True])

    # Создание сводной таблицы
    heatmap_data = df.pivot_table(index="Широта", columns="Долгота", values="Радиационное воздействие метана (Вт/м²)",
                                  aggfunc="mean")

    # Построение тепловой карты с инверсией оси Y
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, cmap="viridis", cbar_kws={"label": "Средний уровень метана (Вт/м²)"}, ax=ax)
    ax.invert_yaxis()  # Инверсия оси Y для правильного отображения широты
    ax.set_title("Тепловая карта концентрации метана")
    ax.set_xlabel("Долгота")
    ax.set_ylabel("Широта")
    st.pyplot(fig)



def compare_regions(df):
    """Сравнение уровней загрязнения по регионам."""
    st.subheader("Сравнение уровней метана по регионам")
    df["Широта"] = df["Координаты Египта (широта, долгота)"].apply(lambda x: float(x.split(",")[0]))
    df["Долгота"] = df["Координаты Египта (широта, долгота)"].apply(lambda x: float(x.split(",")[1]))

    # Группировка по регионам и сортировка по широте и долготе
    region_stats = df.groupby(["Широта", "Долгота"])["Радиационное воздействие метана (Вт/м²)"].mean().reset_index()
    region_stats = region_stats.sort_values(by=["Широта", "Долгота"], ascending=[True, True])

    # Диаграмма баров
    st.subheader("Диаграмма уровней метана по регионам")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=region_stats, x="Долгота", y="Радиационное воздействие метана (Вт/м²)", hue="Широта",
                palette="viridis", dodge=False)
    ax.invert_yaxis()  # Инверсия оси Y для правильного отображения
    plt.xticks(rotation=90)
    ax.set_title("Сравнение уровней метана по регионам")
    ax.set_xlabel("Долгота")
    ax.set_ylabel("Средний уровень метана (Вт/м²)")
    st.pyplot(fig)



def main():
    st.title("Анализ уровней метана в Египте (2003-2018)")

    # Путь к файлу
    file_path = "TableEgyptMetan_2003_2018.csv"

    try:
        # Загрузка данных
        df = pd.read_csv(file_path, index_col=0)
        st.success("Файл успешно загружен!")
        st.dataframe(df)

        # Задача 1: Статистические показатели
        st.header("1. Базовая статистика для уровня метана")
        stats = calculate_statistics(df)
        st.write(stats)

        # Задача 2: График временных рядов
        st.header("2. График временных рядов уровня метана")
        analyze_time_series(df)

        # Задача 3: Тепловая карта
        st.header("3. Тепловая карта концентраций метана")
        heatmap_pollution(df)

        # Задача 4: Сравнение по регионам
        st.header("4. Сравнение уровней метана по регионам")
        compare_regions(df)

    except Exception as e:
        st.error(f"Ошибка при обработке файла: {e}")


if __name__ == "__main__":
    main()
