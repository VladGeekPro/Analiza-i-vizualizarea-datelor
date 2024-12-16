import streamlit as st
import pandas as pd

def main():
    st.title("Объединение данных из двух таблиц")

    # Пути к файлам
    file_path1 = "MergedTableSudanAerosolDioxideCarbon_2003_2018.csv"
    file_path2 = "TableSudanMethane_2003_2018.csv"

    try:
        # Загрузка данных из двух таблиц
        df1 = pd.read_csv(file_path1, index_col=0)
        st.subheader("Первая таблица (исходная):")
        st.dataframe(df1)

        df2 = pd.read_csv(file_path2, index_col=0)
        st.subheader("Вторая таблица:")
        st.dataframe(df2)

        # Проверка на соответствие количества строк
        if len(df1) != len(df2):
            st.error("Ошибка: Количество строк в таблицах не совпадает!")
            return

        # Добавляем третью колонку из второй таблицы в конец первой таблицы
        third_column_name = df2.columns[2]  # Получаем название третьей колонки
        df1[third_column_name] = df2.iloc[:, 2].values

        # Отображение объединённой таблицы
        st.subheader("Объединённая таблица:")
        st.dataframe(df1)

    except Exception as e:
        st.error(f"Ошибка при обработке файла: {e}")

if __name__ == "__main__":
    main()
