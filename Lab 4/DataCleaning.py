import pandas as pd
import streamlit as st

def clean_data(df):
    """Функция для очистки данных: обработка пропусков, преобразование типов и удаление дубликатов."""
    
    st.write("### Преобразование типов данных:")
    # Преобразование колонки points в числовой тип
    if 'points' in df.columns:
        df['points'] = pd.to_numeric(df['points'], errors='coerce')
        st.write("Колонка 'points' успешно преобразована в числовой тип.")
        
        # Проверка на некорректные значения
        nan_count = df['points'].isnull().sum()
        if nan_count > 0:
            st.warning(f"Обнаружено {nan_count} некорректных значений в 'points', они заменены на NaN.")
    
    # Обработка пропущенных значений
    st.write("### Обработка пропущенных значений:")
    missing_values = df.isnull().sum()
    st.write("Количество пропущенных значений до обработки:")
    st.write(missing_values)

    for column in df.columns:
        if df[column].dtype == 'object':  # Текстовые данные
            mode_value = df[column].mode()[0]  # Наиболее часто встречающееся значение
            df[column].fillna(mode_value, inplace=True)
        else:  # Числовые данные
            median_value = df[column].median()  # Медиана
            df[column].fillna(median_value, inplace=True)

    # Проверка на дубликаты
    st.write("\n### Проверка и удаление дубликатов:")
    duplicates_count = df.duplicated().sum()
    st.write(f"Количество дубликатов до удаления: {duplicates_count}")

    df.drop_duplicates(inplace=True)
    st.write(f"Количество дубликатов после удаления: {df.duplicated().sum()}")

    # Итоговая проверка
    st.write("\n### Количество пропущенных значений после обработки:")
    st.write(df.isnull().sum())

    return df


def main():
    st.title("Анализ данных о винах")
    
    # Путь к файлу
    file_path = "./dirty_wine_data.csv"
    
    if file_path is not None:
        # Чтение данных из CSV
        df = pd.read_csv(file_path)

        # Отображение исходных данных
        st.subheader("Исходные данные:")
        st.dataframe(df)

        # Очистка данных
        st.subheader("Очистка данных:")
        cleaned_df = clean_data(df)

        # Отображение очищенных данных
        st.subheader("Очищенные данные:")
        st.dataframe(cleaned_df)

        # Скачать очищенные данные
        st.download_button(
            label="Скачать очищенные данные в формате CSV",
            data=cleaned_df.to_csv(index=False).encode('utf-8'),
            file_name="cleaned_wine_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()