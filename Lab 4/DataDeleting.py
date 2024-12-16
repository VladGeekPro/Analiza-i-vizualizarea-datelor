import pandas as pd

def reduce_csv_size(input_file, output_file, reduction_factor=7):
    """
    Уменьшает размер данных в CSV-файле путем случайного удаления строк.
    
    Args:
        input_file (str): Путь к исходному файлу CSV.
        output_file (str): Путь к файлу, где будет сохранён уменьшенный набор данных.
        reduction_factor (int): Во сколько раз уменьшить размер данных (по умолчанию 7).
    """
    # Загрузка данных из CSVs
    df = pd.read_csv(input_file)

    # Расчет доли строк, которые нужно оставить
    fraction_to_keep = 1 / reduction_factor

    # Случайная выборка строк
    reduced_df = df.sample(frac=fraction_to_keep, random_state=42)

    # Сохранение уменьшенного набора данных
    reduced_df.to_csv(output_file, index=False)
    print(f"Уменьшенный файл сохранён в: {output_file}")

# Пример использования
input_file = "./cleaned_wine_data.csv"
output_file = "./reduced_cleaned_wine_data.csv"  # Уменьшенный файл
reduce_csv_size(input_file, output_file)
