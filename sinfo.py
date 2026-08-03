import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime

# 1. SIVUN ASETUKSET
st.set_page_config(page_title="Mökkisää Äijälä", page_icon="☀️", layout="wide")

# 2. TYYLIKÄS CSS-TYYLITTELY
st.markdown("""
<style>
    /* Koko sovelluksen tausta - tumma ja rauhallinen liukuväri */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #e0e0e0;
    }
    
    /* Otsikoiden tyylittely */
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 300 !important;
        letter-spacing: 1px;
        color: #ffffff !important;
    }

    /* PÄIVÄN YHTEENVETO -KORTIT - Lasimainen tumma tausta */
    div[data-testid="metric-container"] {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Yhteenvedon arvot ja otsikot KIRKKAAN VALKOISEKSI */
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] *,
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: white !important; 
        font-weight: 600 !important;
    }

    /* ILMOITUSLAATIKOT (Success/Error/Warning) - Beigeiksi ja teksti tummaksi */
    div[data-testid="stAlert"] {
        background-color: #E8D8C8 !important;
        border: 1px solid #d1bfae !important;
        border-radius: 12px;
    }
    div[data-testid="stAlert"] p, 
    div[data-testid="stAlert"] span {
        color: #1a1a1a !important; 
        font-weight: 500 !important;
    }

    /* Pudotusvalikon tekstin väri */
    .stSelectbox label {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. HEADER-OSIO
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Äijälä Basecamp</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #dedede; font-size: 1.2rem; margin-bottom: 40px;'>Sääasema ja ulkoiluikkunat</p>", unsafe_allow_html=True)

# 4. DATAN HAKU
@st.cache_data
def hae_saa():
    lat, lon = 62.34, 26.07
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,cloudcover,windspeed_10m&wind_speed_unit=ms&timezone=Europe%2FHelsinki"
    
    try:
        data = requests.get(url, timeout=10).json()
        df = pd.DataFrame({
            "Aika": pd.to_datetime(data["hourly"]["time"]),
            "Lämpötila (°C)": data["hourly"]["temperature_2m"],
            "Sade (mm)": data["hourly"]["precipitation"],
            "Pilvisyys (%)": data["hourly"]["cloudcover"],
            "Tuuli (m/s)": data["hourly"]["windspeed_10m"]
        })
        return df
    except:
        return pd.DataFrame()

df = hae_saa()

if not df.empty:
    nykyhetki = pd.Timestamp.now()
    df = df[df["Aika"] >= nykyhetki]

    # Päivänvalinta
    col_empty1, col_selector, col_empty2 = st.columns([1, 2, 1])
    with col_selector:
        kaikki_paivat = df["Aika"].dt.date.unique()
        # Otetaan koko viikko (esimerkiksi 7 päivää tai kaikki mitä API tarjoaa)
        valittu_paiva = st.selectbox("VALITSE PÄIVÄ:", kaikki_paivat)

    paivan_data = df[df["Aika"].dt.date == valittu_paiva]

    # 5. PÄIVÄN YHTEENVETO
    st.write("### Päivän yhteenveto")
    m1, m2, m3, m4 = st.columns(4)
    
    max_temp = paivan_data["Lämpötila (°C)"].max()
    min_temp = paivan_data["Lämpötila (°C)"].min()
    total_rain = paivan_data["Sade (mm)"].sum()
    max_wind = paivan_data["Tuuli (m/s)"].max()

    m1.metric("Lämpöhuippu", f"{max_temp:.1f} °C")
    m2.metric("Alin lämpötila", f"{min_temp:.1f} °C")
    m3.metric("Kokonaissade", f"{total_rain:.1f} mm")
    m4.metric("Kovin tuuli", f"{max_wind:.1f} m/s")

    st.divider()

    # 6. PÄÄASETTELU: KAKSI ISOA SARAKETTA
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.write("### Sääennuste")
        st.write("🌡️ **Lämpötila**")
        kuvaaja_data = paivan_data[["Aika", "Lämpötila (°C)"]]

        lampo_chart = alt.Chart(kuvaaja_data).mark_area(
            color="#b33939", opacity=0.85
        ).encode(
            x=alt.X("Aika:T", axis=alt.Axis(title=None)),
            y=alt.Y("Lämpötila (°C):Q", axis=alt.Axis(title=None))
        ).properties(height=200).configure_view(
            fill="#E8D8C8", strokeWidth=0
        ).configure(
            background="#E8D8C8"
        ).configure_axis(
            labelColor="#1a1a1a", gridColor="#d1bfae"
        )
        st.altair_chart(lampo_chart, use_container_width=True)

        st.write("🌧️ **Sademäärä**")
        sade_data = paivan_data[["Aika", "Sade (mm)"]]

        sade_chart = alt.Chart(sade_data).mark_bar(
            color="#227093"
        ).encode(
            x=alt.X("Aika:T", axis=alt.Axis(title=None)),
            y=alt.Y("Sade (mm):Q", axis=alt.Axis(title=None))
        ).properties(height=200).configure_view(
            fill="#E8D8C8", strokeWidth=0
        ).configure(
            background="#E8D8C8"
        ).configure_axis(
            labelColor="#1a1a1a", gridColor="#d1bfae"
        )
        st.altair_chart(sade_chart, use_container_width=True)

    with right_col:
        st.write("### Optimaaliset ulkoiluikkunat")
        
        pouta_tunnit = paivan_data[paivan_data["Sade (mm)"] == 0].copy()
        
        if pouta_tunnit.empty:
            st.error("🌧️ Jatkuvaa sadetta havaittu. Terassikeli on peruttu.")
        else:
            paras_tunti = pouta_tunnit.loc[pouta_tunnit["Lämpötila (°C)"].idxmax()]
            st.success(f"☀️ Päivän paras hetki: Kello {paras_tunti['Aika'].strftime('%H:%M')} (Lämpötila: {paras_tunti['Lämpötila (°C)']} °C, Tuuli: {paras_tunti['Tuuli (m/s)']} m/s)")
            
            pouta_tunnit["Kello"] = pouta_tunnit["Aika"].dt.strftime('%H:%M')
            siistitty_taulukko = pouta_tunnit[["Kello", "Lämpötila (°C)", "Tuuli (m/s)", "Pilvisyys (%)"]].set_index("Kello")
            
            # Taulukko täysin beigeksi ja ruskein reunoin
            tummataulukko = siistitty_taulukko.style.set_properties(**{
                'background-color': '#E8D8C8',
                'color': '#1a1a1a',
                'border': '1px solid #d1bfae',
                'font-weight': '500'
            }).set_table_styles([
                {'selector': 'th, td', 'props': [
                    ('background-color', '#E8D8C8'),
                    ('color', '#1a1a1a'),
                    ('border', '1px solid #d1bfae'),
                ]},
                {'selector': 'table', 'props': [
                    ('border-collapse', 'collapse'),
                    ('background-color', '#E8D8C8'),
                    ('border', '1px solid #d1bfae'),
                    ('width', '100%')
                ]}
            ])
            
            st.markdown(tummataulukko.to_html(), unsafe_allow_html=True)
else:
    st.error("Datan lataus epäonnistui.")