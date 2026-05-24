import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Аналитика Недвижимости СПб", layout="wide")
st.title("Рынок жилой недвижимости СПб")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("syntethic_data.csv")
        # Приводим к числам, убираем битые строки
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["area"] = pd.to_numeric(df["area"], errors="coerce")
        df["reputation_score"] = pd.to_numeric(df["reputation_score"], errors="coerce")
        df.dropna(inplace=True)
        return df
    except FileNotFoundError:
        st.error("❌ Файл data.csv не найден. Положите его в ту же папку, что и app.py")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.sidebar.header("🔍 Фильтры")
    
    min_price, max_price = st.sidebar.slider(
        "Бюджет (млн ₽)", 
        int(df["price"].min()/1e6), 
        int(df["price"].max()/1e6), 
        (int(df["price"].min()/1e6), int(df["price"].max()/1e6))
    )
    
    min_rep = st.sidebar.slider("Мин. индекс репутации", 0, 100, 0)

    filtered_df = df[
        (df["price"] >= min_price*1e6) & 
        (df["price"] <= max_price*1e6) & 
        (df["reputation_score"] >= min_rep)
    ]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Карта объектов")
        m = folium.Map(location=[59.9343, 30.3351], zoom_start=11)
        for _, row in filtered_df.iterrows():
            color = "green" if row["reputation_score"] > 70 else "red"
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=8,
                color=color,
                fill=True,
                fill_color=color,
                popup=f"<b>{row['address']}</b><br>Цена: {row['price']//1000000} млн ₽<br>Рейтинг: {row['reputation_score']}"
            ).add_to(m)
        st_folium(m, width=700, height=500)

    with col2:
        st.subheader("Таблица выборки")
        st.dataframe(filtered_df[["address", "price", "area", "rooms", "reputation_score"]])
        st.download_button(
            label="📥 Скачать текущую выборку в CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_real_estate.csv",
            mime="text/csv"
        )
else:
    st.info("⏳ Ожидание файла data.csv...")