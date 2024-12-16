import pandas as pd
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer

@st.cache_data
def load_data(file_path):
    """Загрузка данных с использованием кэширования."""
    return pd.read_csv(file_path)


def calculate_numeric_statistics(df):
    """Вычисляет статистики для числовых колонок."""
    st.markdown("### :bar_chart: Статистики для числовых переменных")
    numeric_columns = ["price", "points", "alcohol"]  # Выбираем нужные числовые колонки
    stats = df[numeric_columns].describe().style.format("{:.2f}")
    st.table(stats)

def add_price_quality_ratio(df):
    """Добавляет колонку с соотношением цена/качество."""
    df["price_quality_ratio"] = df["price"] / df["points"]
    return df

def filter_by_price_quality(df):
    """Фильтрация данных по соотношению цена/качество."""
    st.sidebar.markdown("### :mag: Фильтрация по соотношению цена/качество")
    min_ratio = st.sidebar.slider(
        "Минимальное соотношение", float(df["price_quality_ratio"].min()), float(df["price_quality_ratio"].max()), float(df["price_quality_ratio"].min())
    )
    max_ratio = st.sidebar.slider(
        "Максимальное соотношение", float(df["price_quality_ratio"].min()), float(df["price_quality_ratio"].max()), float(df["price_quality_ratio"].max())
    )
    filtered_df = df[(df["price_quality_ratio"] >= min_ratio) & (df["price_quality_ratio"] <= max_ratio)]
    st.markdown("### :clipboard: Отфильтрованные данные по соотношению цена/качество")
    st.dataframe(filtered_df)
    return filtered_df

def explore_categorical_variables(df):
    """Анализ распределения для категориальных переменных."""
    st.markdown("### Распределение для категориальных переменных")

    # Распределение по странам
    st.markdown("#### Количество вин по странам")
    country_counts = df["country"].value_counts()
    if not country_counts.empty:
        st.bar_chart(country_counts)
    else:
        st.warning("Нет данных для отображения по странам.")

    # Распределение по категориям вин
    st.markdown("#### Количество вин по категориям")
    category_counts = df["category"].value_counts()
    if not category_counts.empty:
        st.bar_chart(category_counts)
    else:
        st.warning("Нет данных для отображения по категориям.")

    # Распределение по сортам винограда
    st.markdown("#### Количество вин по сортам винограда (топ-10)")
    variety_counts = df["variety"].value_counts().head(10)  # Топ-10 сортов
    if not variety_counts.empty:
        st.bar_chart(variety_counts)
    else:
        st.warning("Нет данных для отображения по сортам винограда.")
    
def plot_points_distribution(df):
    """Гистограмма для распределения points."""
    st.markdown("### :bar_chart: Распределение баллов (points)")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df["points"], bins=20, kde=True, ax=ax, color="blue")
    ax.set_title("Распределение баллов")
    ax.set_xlabel("Баллы")
    ax.set_ylabel("Количество вин")
    st.pyplot(fig)

def plot_average_price_by_country(df):
    """Средние цены по странам."""
    st.markdown("### :bar_chart: Средние цены по странам")
    avg_price_country = df.groupby("country")["price"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(12, 8))
    avg_price_country.plot(kind="bar", color="green", ax=ax)
    ax.set_title("Средние цены по странам")
    ax.set_ylabel("Средняя цена (USD)")
    ax.set_xlabel("Страна")
    st.pyplot(fig)

def plot_category_region_distribution(df):
    """Составной столбчатый график для категорий и регионов."""
    st.markdown("### :bar_chart: Распределение вин по категориям и регионам")
    if "category" in df.columns and "region_1" in df.columns:
        category_region_counts = pd.crosstab(df["region_1"], df["category"])
        fig, ax = plt.subplots(figsize=(14, 8))
        category_region_counts.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
        ax.set_title("Распределение вин по категориям и регионам")
        ax.set_xlabel("Регион")
        ax.set_ylabel("Количество вин")
        st.pyplot(fig)
    else:
        st.warning("Данные о категориях или регионах отсутствуют.")


def analyze_description(df):
    """Анализ описаний вин."""
    st.markdown("### :speech_balloon: Анализ описаний вин")

    # Удаление общих слов
    common_words = {"and", "the", "is", "of", "a", "in", "this", "with", "on", "to", "s", "that", "it", "but", "from"}
    descriptions = df["description"].dropna().str.lower()
    words = re.findall(r'\b\w+\b', " ".join(descriptions))
    filtered_words = [word for word in words if word not in common_words]

    # Частота слов
    word_counts = Counter(filtered_words)
    most_common_words = word_counts.most_common(10)
    st.write("**Топ-10 самых частых слов в описаниях:**")
    st.write(pd.DataFrame(most_common_words, columns=["Слово", "Частота"]))

    # Средняя длина описаний
    description_lengths = descriptions.str.split().str.len()
    avg_length = description_lengths.mean()
    st.write(f"**Средняя длина описания:** {avg_length:.2f} слов")


def generate_wordcloud(df):
    """Генерация облака слов."""
    st.markdown("### :cloud: Облако слов из описаний вин")

    descriptions = df["description"].dropna().str.lower()
    wordcloud_text = " ".join(descriptions)

    # Генерация облака слов
    wordcloud = WordCloud(
        width=800, height=400, background_color="white"
    ).generate(wordcloud_text)

    # Отображение
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

def word_correlation_analysis(df):
    """Анализ корреляции наиболее частых слов с ценой, рейтингом и сортами."""
    st.markdown("### :bar_chart: Анализ корреляции слов")
    
    # Извлечение описаний
    descriptions = df["description"].dropna().values
    if len(descriptions) == 0:
        st.warning("Нет данных для анализа корреляции слов.")
        return

    # Создание матрицы частот слов
    vectorizer = CountVectorizer(max_features=100, stop_words="english")
    word_matrix = vectorizer.fit_transform(descriptions)
    word_df = pd.DataFrame(word_matrix.toarray(), columns=vectorizer.get_feature_names_out())
    
    # Добавление числовых колонок
    word_df["price"] = df["price"].reset_index(drop=True)
    word_df["points"] = df["points"].reset_index(drop=True)

    # Корреляция слов с ценой и рейтингом
    st.markdown("#### Корреляция слов с ценой и рейтингом")
    correlation_matrix = word_df.corr()
    price_corr = correlation_matrix["price"].sort_values(ascending=False).head(10)
    points_corr = correlation_matrix["points"].sort_values(ascending=False).head(10)
    
    st.write("Наиболее коррелирующие слова с ценой:")
    st.dataframe(price_corr)
    
    st.write("Наиболее коррелирующие слова с рейтингом:")
    st.dataframe(points_corr)

    # Scatter plots
    st.markdown("#### Scatter plots для корреляций")
    scatter_words = list(price_corr.index[:5]) + list(points_corr.index[:5])  # Топ-5 коррелирующих слов с ценой и рейтингом
    for word in scatter_words:
        if word in word_df.columns:
            fig, ax = plt.subplots(1, 2, figsize=(14, 6))
            
            # Scatter с ценой
            ax[0].scatter(word_df[word], word_df["price"], alpha=0.6, color="blue")
            ax[0].set_title(f"Связь {word} с ценой")
            ax[0].set_xlabel(f"Частота слова {word}")
            ax[0].set_ylabel("Цена")
            
            # Scatter с рейтингом
            ax[1].scatter(word_df[word], word_df["points"], alpha=0.6, color="green")
            ax[1].set_title(f"Связь {word} с рейтингом")
            ax[1].set_xlabel(f"Частота слова {word}")
            ax[1].set_ylabel("Рейтинг")
            
            st.pyplot(fig)

    # Корреляция с сортами винограда
    st.markdown("#### Анализ корреляции слов с сортами винограда")
    if "variety" in df.columns:
        varieties = df["variety"].fillna("Unknown")
        word_df["variety"] = varieties.reset_index(drop=True)
        word_variety_corr = (
            word_df.groupby("variety")
            .mean()
            .corr(method="pearson")
            .iloc[:, :-1]  # Убираем столбец variety
        )
        
        st.markdown("Корреляция слов с сортами винограда (первые 10):")
        st.dataframe(word_variety_corr.head(10))

        # Визуализация heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(word_variety_corr, cmap="coolwarm", annot=False)
        st.pyplot(plt)
    else:
        st.warning("Колонка 'variety' отсутствует для анализа корреляции.")


def main():
    st.set_page_config(page_title="Wine Data Analysis", layout="wide", page_icon=":wine_glass:")

    st.markdown("# :wine_glass: Исследование данных о винах")
    st.markdown(
        """
        Добро пожаловать! Здесь вы можете изучить данные о винах, их распределение по категориям, странам и получить статистику. 
        Также анализируется текстовое описание вин и генерируется облако слов.
        """
    )

    # Путь к обработанному файлу
    file_path = "./reduced_cleaned_wine_data.csv"

    try:
        # Загрузка данных из CSV
        df = load_data(file_path)

        # Добавление соотношения цена/качество
        df = add_price_quality_ratio(df)

        # Фильтр по стране
        st.sidebar.markdown("### :globe_with_meridians: Фильтр по стране")
        unique_countries = df["country"].unique()
        default_countries = unique_countries[:10] if len(unique_countries) > 10 else unique_countries
        country_filter = st.sidebar.multiselect(
            "Выберите страну:", options=unique_countries, default=default_countries
        )
        if country_filter:
            df = df[df["country"].isin(country_filter)]

        # Фильтрация по соотношению цена/качество
        df = filter_by_price_quality(df)

        # 1. Статистики для числовых переменных
        calculate_numeric_statistics(df)

        # 2. Распределение для категориальных переменных
        explore_categorical_variables(df)

        # 3. Анализ описаний вин
        if st.sidebar.checkbox("Анализ описаний вин", value=True):
            analyze_description(df)
        
        # 4. Распределение points
        plot_points_distribution(df)

        # 5. Средние цены по странам
        plot_average_price_by_country(df)

        # 6. Распределение категорий и регионов
        plot_category_region_distribution(df)

        # 7. Облако слов
        if st.sidebar.checkbox("Показать облако слов", value=True):
            generate_wordcloud(df)

        # 8. Анализ корреляции
        st.sidebar.markdown("### :chart_with_upwards_trend: Анализ корреляции")
        if st.sidebar.checkbox("Анализ корреляции слов", value=True):
            word_correlation_analysis(df)

    except Exception as e:
        st.error(f"Ошибка при обработке данных: {e}")


if __name__ == "__main__":
    main()
