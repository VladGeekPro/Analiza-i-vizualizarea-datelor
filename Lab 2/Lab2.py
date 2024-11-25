import matplotlib.patches as mpatches
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from shapely.geometry import Point

# Настройка страницы
st.set_page_config(page_title="Dashboard Rezultatele Alegerilor", layout="wide")

# Таблица 1: Rezultatele alegerilor prezidențiale
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>Rezultatele Alegerilor pentru Funcția de Președinte</h1>", unsafe_allow_html=True)
st.divider()
file_path_alegeri = 'Выборы.xlsx'

columns_mapping = {
    'Localitatea': 'Localitate',
    'd) numărul de alegători \ncare au participat \nla votare': 'Numărul de alegători care au participat la votare',
    'h) numărul total de\n voturi valabil exprimate': 'Total voturi valabil exprimate',
    'Stoianoglo \nAlexandr': 'Alexandr Stoianoglo',
    'Sandu \nMaia': 'Maia Sandu',
    'Usatîi\nRenato': 'Renato Usatii',
    'Tarlev\nVasile': 'Vasile Tarlev',
    'Vlah\nIrina': 'Irina Vlah',
    'Chicu\nIon': 'Ion Chicu',
    'Năstase\nAndrei': 'Andrei Nastase',
    'Țîcu\nOctavian': 'Octavian Ticu',
    'Furtună\nVictoria': 'Victoria Furtuna',
    'Ulianovschi\nTudor': 'Tudor Ulianovschi',
    'Morari\nNatalia': 'Natalia Morari'
}

data_alegeri = pd.read_excel(file_path_alegeri, sheet_name=0)
data_alegeri = data_alegeri.rename(columns=columns_mapping)
data_alegeri = data_alegeri[list(columns_mapping.values())]

data_filtered = data_alegeri[~data_alegeri['Localitate'].str.contains('Circumscrip|Alegeri prezidențiale', na=True)]
for column in data_filtered.columns[1:]:
    data_filtered[column] = pd.to_numeric(data_filtered[column], errors='coerce')
data_grouped = data_filtered.groupby('Localitate').sum().reset_index()

st.write(data_grouped)

# Графики для таблицы 1
with st.expander("Distribuția voturilor pe candidați"):
    st.markdown("<h3 style='color: #32CD32;'>Distribuția Voturilor pe Candidați</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    filtered_data = data_grouped.drop(columns=['Numărul de alegători care au participat la votare',
                                               'Total voturi valabil exprimate'])
    filtered_data.iloc[:, 1:].sum().plot(kind='bar', ax=ax)
    ax.set_ylabel("Număr de voturi")
    plt.tight_layout()
    st.pyplot(fig)

with st.expander("Top 5 localități cu cele mai multe voturi exprimate"):
    st.markdown("<h3 style='color: #32CD32;'>Top 5 localități cu cele mai multe voturi exprimate</h3>", unsafe_allow_html=True)
    top5 = data_grouped.nlargest(5, 'Total voturi valabil exprimate')
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=top5, x='Localitate', y='Total voturi valabil exprimate', ax=ax, palette='dark')
    plt.tight_layout()
    st.pyplot(fig)

# Таблица 2: Populația pe raioane, grupe de vârstă și sexe
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>Populația pe Raioane și Grupe de Vârstă</h1>", unsafe_allow_html=True)
st.divider()
file_path_populatie = 'pop010400rclreg_20241110-194246.xlsx'

data_populatie = pd.read_excel(file_path_populatie, header=None, skiprows=3, usecols="A:D")
data_populatie.columns = ['Localitate', 'Vârstă', 'Gen', 'Valoare']
data_populatie['Localitate'].fillna(method='ffill', inplace=True)
data_populatie['Vârstă'].fillna(method='ffill', inplace=True)
data_populatie['Valoare'] = pd.to_numeric(data_populatie['Valoare'], errors='coerce')
st.write(data_populatie)

# Графики для таблицы 2
with st.expander("Distribuția populației pe grupe de vârstă"):
    st.markdown("<h3 style='color: #32CD32;'>Distribuția Populației pe Grupe de Vârstă</h3>", unsafe_allow_html=True)
    age_order = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39',
                 '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75 peste']
    aggregated_data = data_populatie.groupby(['Vârstă', 'Gen'])['Valoare'].sum().reset_index()
    aggregated_data['Vârstă'] = pd.Categorical(aggregated_data['Vârstă'], categories=age_order, ordered=True)
    aggregated_data = aggregated_data.sort_values('Vârstă')
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=aggregated_data, x='Vârstă', y='Valoare', hue='Gen', ax=ax, palette='dark', ci=None)
    ax.set_ylabel("Populație")
    plt.tight_layout()
    st.pyplot(fig)

with st.expander("Top 5 grupe de vârstă cu cea mai mare populație"):
    st.markdown("<h3 style='color: #32CD32;'>Top 5 grupe de vârstă cu cea mai mare populație</h3>", unsafe_allow_html=True)
    top5_age = data_populatie.groupby('Vârstă')['Valoare'].sum().nlargest(5).reset_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=top5_age, x='Vârstă', y='Valoare', ax=ax, palette='dark')
    plt.tight_layout()
    st.pyplot(fig)

# Таблица 3: Populația pe regiuni statistice
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>Populația pe regiuni statistice, relația cu piața forței de muncă și grupe de vârstă (2023)</h1>", unsafe_allow_html=True)
st.divider()
file_path_regiuni = 'mun010900reg_20241117-163538.xlsx'

data_regiuni = pd.read_excel(file_path_regiuni, header=None, skiprows=3, usecols="A:F")
data_regiuni.columns = ['Localitate', 'Relația cu piața forței de muncă', 'Nivel de instruire', 'Gen', 'Grupe de vârstă', 'Valoare']
data_regiuni['Localitate'].fillna(method='ffill', inplace=True)
data_regiuni['Relația cu piața forței de muncă'].fillna(method='ffill', inplace=True)
data_regiuni['Nivel de instruire'].fillna(method='ffill', inplace=True)
data_regiuni['Gen'].fillna(method='ffill', inplace=True)
data_regiuni['Valoare'] = pd.to_numeric(data_regiuni['Valoare'], errors='coerce')
data_regiuni = data_regiuni.dropna(subset=['Grupe de vârstă'])
st.write(data_regiuni)

# Графики для таблицы 3
with st.expander("Distribuția populației pe regiuni"):
    st.markdown("<h3 style='color: #32CD32;'>Distribuția populației pe regiuni</h3>",
                unsafe_allow_html=True)
    grouped_data = data_regiuni.groupby(['Localitate', 'Gen'])['Valoare'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=grouped_data, x='Localitate', y='Valoare', hue='Gen', ax=ax, palette='dark', ci=None)
    ax.set_ylabel("Populație")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

with st.expander("Distribuția populației în funcție de nivelul de instruire"):
    st.markdown("<h3 style='color: #32CD32;'>Distribuția populației în funcție de nivelul de instruire</h3>",
                unsafe_allow_html=True)
    grouped_by_instruire = data_regiuni.groupby(['Localitate', 'Nivel de instruire'])['Valoare'].sum().reset_index()
    top5_regions = grouped_by_instruire.groupby('Localitate')['Valoare'].sum().nlargest(5).reset_index()
    top5_data = grouped_by_instruire[grouped_by_instruire['Localitate'].isin(top5_regions['Localitate'])]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=top5_data, x='Localitate', y='Valoare', hue='Nivel de instruire', ax=ax, palette='dark', ci=None)
    ax.set_ylabel("Populație")
    ax.set_xlabel("Regiuni")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# Загрузка координат из файла JSON
with open('coordinates.json', 'r') as file:
    coordinates_data = json.load(file)

# Преобразование JSON в DataFrame
coordinates_df = pd.DataFrame(coordinates_data)

# Сопоставление координат с районами
def get_coordinates(localitate):
    match = coordinates_df[coordinates_df['city'] == localitate]
    if not match.empty:
        return Point(match.iloc[0]['longitude'], match.iloc[0]['latitude'])
    else:
        return None  # Возврат None, если координаты не найдены

# Определение топ-3 кандидатов по сумме голосов
candidate_votes = data_grouped.drop(columns=['Numărul de alegători care au participat la votare',
                                             'Total voturi valabil exprimate']).iloc[:, 1:]
top_3_candidates = candidate_votes.sum().nlargest(3).index

# Фильтрация данных только для топ-3 кандидатов
data_top3 = data_grouped[['Localitate'] + list(top_3_candidates)]

# Определение победителя среди топ-3 кандидатов в каждом районе
data_top3['Candidat câștigător'] = data_top3.iloc[:, 1:].idxmax(axis=1)

# Добавление геометрии на основе координат
data_top3['geometry'] = data_top3['Localitate'].apply(get_coordinates)

# Удаление записей с отсутствующими координатами
data_top3 = data_top3.dropna(subset=['geometry'])

# Преобразование в GeoDataFrame
gdf = gpd.GeoDataFrame(data_top3, geometry='geometry')

# Создание цветовой схемы для топ-3 кандидатов
candidate_colors = {
    top_3_candidates[0]: 'red',
    top_3_candidates[1]: 'blue',
    top_3_candidates[2]: 'green'
}
gdf['color'] = gdf['Candidat câștigător'].map(candidate_colors)

# Построение карты
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>Distribuția voturilor pe hartă pentru top-3 candidați</h1>", unsafe_allow_html=True)
st.divider()
st.write(data_top3)
fig, ax = plt.subplots(1, 1, figsize=(10, 5))

# Отображение точек с цветовой кодировкой
gdf.plot(ax=ax, color=gdf['color'], edgecolor='black')

# Добавление легенды
patches = [
    mpatches.Patch(color='red', label=f'{top_3_candidates[0]}'),
    mpatches.Patch(color='blue', label=f'{top_3_candidates[1]}'),
    mpatches.Patch(color='green', label=f'{top_3_candidates[2]}')
]
legend = ax.legend(handles=patches, loc='lower left', title="Candidați", fontsize=10, frameon=True)

# Настройка отступов легенды от карты
legend.get_frame().set_edgecolor('black')  # Обводка рамки
legend.get_frame().set_linewidth(0.5)  # Толщина обводки рамки

plt.tight_layout()
st.pyplot(fig)