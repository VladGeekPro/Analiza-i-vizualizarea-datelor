import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    data_path = 'DataSistemulEnergetic.csv'
    data = pd.read_csv(data_path)
    return data

data = load_data()

data['date'] = pd.to_datetime(data['date'])
data['hour'] = data['date'].dt.hour
data['day_of_week'] = data['date'].dt.day_name()
data['month'] = data['date'].dt.month

energy_types = ['carbune', 'hidro', 'hidrocarburi', 'nuclear', 'eolian', 'fotovolt', 'biomasa']

st.title("Tabloul de bord al distribuției energiei")
st.markdown("""
    ## Explorați distribuția tipurilor de energie
    Acest tablou de bord interactiv vizualizează distribuția diferitelor tipuri de energie pe întreaga perioadă a datasetului.
""")

st.subheader("Prezentare generală a datelor")
st.write(data[['date', 'productie', 'sold'] + energy_types])

st.subheader("Distribuția energiei pe tipuri")
selected_types = st.multiselect("Selectați tipurile de energie pentru afișare:", options=energy_types, default=energy_types)

fig, ax = plt.subplots(figsize=(10, 6))
for energy_type in selected_types:
    ax.plot(data['date'], data[energy_type], label=energy_type)

ax.set_xlabel("Dată")
ax.set_ylabel("Valoarea energiei")
ax.set_title("Distribuția energiei în timp")
ax.legend()
st.pyplot(fig)

st.subheader("Diagrama circulare volumitrica a distribuției energiei (valori totale)")
total_values = data[selected_types].sum()
fig, ax = plt.subplots()
ax.pie(total_values, labels=total_values.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

st.subheader("Valori maxime pe oră, zi a săptămânii și lună")

hourly_peaks = data.groupby('hour')[selected_types].max()
fig, ax = plt.subplots(figsize=(10, 6))
hourly_peaks.plot(kind='bar', ax=ax)
ax.set_xlabel("Ora")
ax.set_ylabel("Valoarea maximă a energiei")
ax.set_title("Valori maxime pe oră pentru fiecare tip de energie")
st.pyplot(fig)

daily_peaks = data.groupby('day_of_week')[selected_types].max()
fig, ax = plt.subplots(figsize=(10, 6))
daily_peaks.loc[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']].plot(kind='bar', ax=ax)
ax.set_xlabel("Ziua săptămânii")
ax.set_ylabel("Valoarea maximă a energiei")
ax.set_title("Valori maxime pe ziua săptămânii pentru fiecare tip de energie")
st.pyplot(fig)

monthly_peaks = data.groupby('month')[selected_types].max()
fig, ax = plt.subplots(figsize=(10, 6))
monthly_peaks.plot(kind='bar', ax=ax)
ax.set_xlabel("Luna")
ax.set_ylabel("Valoarea maximă a energiei")
ax.set_title("Valori maxime pe lună pentru fiecare tip de energie")
st.pyplot(fig)

st.subheader("Serii temporale comparative pe oră, zi a săptămânii și lună pentru fiecare tip de energie")

hourly_series = data.groupby('hour')[selected_types].mean()
fig, ax = plt.subplots(figsize=(10, 6))
hourly_series.plot(ax=ax)
ax.set_xlabel("Ora")
ax.set_ylabel("Valoarea medie a energiei")
ax.set_title("Valoarea medie a energiei pe oră pentru fiecare tip de energie")
st.pyplot(fig)

daily_series = data.groupby('day_of_week')[selected_types].mean()
fig, ax = plt.subplots(figsize=(10, 6))
daily_series.loc[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']].plot(ax=ax)
ax.set_xlabel("Ziua săptămânii")
ax.set_ylabel("Valoarea medie a energiei")
ax.set_title("Valoarea medie a energiei pe ziua săptămânii pentru fiecare tip de energie")
st.pyplot(fig)

monthly_series = data.groupby('month')[selected_types].mean()
fig, ax = plt.subplots(figsize=(10, 6))
monthly_series.plot(ax=ax)
ax.set_xlabel("Luna")
ax.set_ylabel("Valoarea medie a energiei")
ax.set_title("Valoarea medie a energiei pe lună pentru fiecare tip de energie")
st.pyplot(fig)
