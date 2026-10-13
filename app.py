import streamlit as st
import pandas as pd
import random

# Link do tvoje Google Sheets tabele
SHEET_ID = "1mzbSkLBLwW9hCN6KSdWiLvYYiaaHoVtXV1xAkXI95XA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="Učenje Italijanskog", page_icon="🇮🇹", layout="centered")

# CSS koji direktno targetira sve nivoe dugmadi i kartica
st.markdown("""
<style>
    /* Zeleno dugme za karticu reči */
    div[data-testid="stButton"] > button.green-card {
        background-color: #2e7d32 !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 25px !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
    }
    
    /* Dugme ✓ Savladana (Zeleno) */
    div.stButton > button[kind="primary"] {
        background-color: #2e7d32 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #1b5e20 !important;
    }

    /* Dugme ✗ Nesavladana (Crveno) */
    div.stButton > button[kind="secondary"] {
        background-color: #c62828 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #b71c1c !important;
    }
</style>
""", unsafe_allow_html=True)

# Učitavanje podataka
@st.cache_data(ttl=2)
def ucitaj_podatke():
    try:
        df = pd.read_csv(SHEET_URL)
        if 'Savladano/Nesavladano' not in df.columns:
            df['Savladano/Nesavladano'] = 'Nesavladano'
        else:
            df['Savladano/Nesavladano'] = df['Savladano/Nesavladano'].fillna('Nesavladano')
        return df
    except Exception as e:
        st.error(f"Greška pri učitavanju tabele: {e}")
        return pd.DataFrame()

# Inicijalizacija podataka
if "df" not in st.session_state:
    st.session_state.df = ucitaj_podatke()

sve_lekcije_list = sorted(st.session_state.df['Lekcija'].unique().tolist()) if not st.session_state.df.empty else []

if "izabrane_lekcije" not in st.session_state or not st.session_state.izabrane_lekcije:
    st.session_state.izabrane_lekcije = sve_lekcije_list

if "prikazi_prevod" not in st.session_state:
    st.session_state.prikazi_prevod = False

if "trenutna_rec" not in st.session_state:
    st.session_state.trenutna_rec = None

# Meni za navigaciju
st.sidebar.title("🇮🇹 Meni")
izbor_menija = st.sidebar.radio("Izaberite opciju:", ["▶ Provera znanja", "📚 Izbor lekcija", "📋 Pregled reči"])

# --- 1. PROVERA ZNANJA ---
if izbor_menija == "▶ Provera znanja":
    st.title("🇮🇹 Provera znanja")
    
    df = st.session_state.df
    izabrane = st.session_state.izabrane_lekcije
    
    filtrirano = df[(df['Lekcija'].isin(izabrane)) & (df['Savladano/Nesavladano'] == 'Nesavladano')]
    
    if filtrirano.empty:
        st.success("🎉 Bravo! Prešli ste sve nesavladane reči iz izabranih lekcija!")
    else:
        if st.session_state.trenutna_rec is None or st.button("🔄 Sledeća reč"):
            st.session_state.prikazi_prevod = False
            slucajni_idx = random.choice(filtrirano.index.tolist())
            st.session_state.trenutna_rec = filtrirano.loc[slucajni_idx]
            st.session_state.trenutni_idx = slucajni_idx
            st.session_state.smer = random.choice(['IT_SRB', 'SRB_IT'])

        rec_podaci = st.session_state.trenutna_rec
        smer = st.session_state.smer
        
        if smer == 'IT_SRB':
            prikaz_rec = rec_podaci['Reč (lema, sa članom)']
            jezik = "Italijanski"
        else:
            prikaz_rec = rec_podaci['Prevod na srpski']
            jezik = "Srpski"

        st.caption(f"Reč na jeziku: **{jezik}**")
        
        if not st.session_state.prikazi_prevod:
            # Kartica sa zelenom pozadinom
            st.markdown(
                f"""
                <div style="background-color: #2e7d32; color: white; padding: 25px; border-radius: 12px; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 15px;">
                    🗣️ {prikaz_rec}
                </div>
                """, 
                unsafe_allow_html=True
            )
            if st.button("💡 Klikni ovde za prevod", use_container_width=True):
                st.session_state.prikazi_prevod = True
                st.rerun()
        else:
            st.info(
                f"🇮🇹 **Italijanski:** {rec_podaci['Reč (lema, sa članom)']}\n\n"
                f"🇷🇸 **Prevod:** {rec_podaci['Prevod na srpski']}\n\n"
                f"📌 **Vrsta:** {rec_podaci['Vrsta reči']} | 📖 **Lekcija:** {rec_podaci['Lekcija']}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Savladana", use_container_width=True, type="primary"):
                    st.session_state.df.at[st.session_state.trenutni_idx, 'Savladano/Nesavladano'] = 'Savladano'
                    st.session_state.trenutna_rec = None
                    st.session_state.prikazi_prevod = False
                    st.rerun()
            with col2:
                if st.button("✗ Nesavladana", use_container_width=True, type="secondary"):
                    st.session_state.trenutna_rec = None
                    st.session_state.prikazi_prevod = False
                    st.rerun()

# --- 2. IZBOR LEKCIJA ---
elif izbor_menija == "📚 Izbor lekcija":
    st.title("📚 Izbor lekcija za proveru")
    
    sve_lekcije = sorted(st.session_state.df['Lekcija'].unique().tolist())
    
    # Multiselect opcija umesto pojedinačnih checkbox-ova za pouzdanije pamćenje
    izabrane_temp = st.multiselect(
        "Izaberite lekcije koje želite da učite:",
        options=sve_lekcije,
        default=st.session_state.izabrane_lekcije
    )
    
    if st.button("Sačuvaj izbor", type="primary"):
        if not izabrane_temp:
            st.warning("Morate izabrati makar jednu lekciju!")
        else:
            st.session_state.izabrane_lekcije = izabrane_temp
            st.success("Izbor lekcija sačuvan za trenutnu sesiju!")

# --- 3. PREGLED REČI ---
elif izbor_menija == "📋 Pregled reči":
    st.title("📋 Pregled reči")
    
    status_filter = st.radio("Prikaži:", ["Savladane", "Nesavladane"], horizontal=True)
    izabrani_status = "Savladano" if status_filter == "Savladane" else "Nesavladano"
    novi_status = "Nesavladano" if izabrani_status == "Savladano" else "Savladano"
    
    df_prikaz = st.session_state.df[st.session_state.df['Savladano/Nesavladano'] == izabrani_status]
    
    st.dataframe(
        df_prikaz[['Lekcija', 'Reč (lema, sa članom)', 'Prevod na srpski', 'Vrsta reči']],
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    st.subheader("🔄 Promena statusa reči")
    
    if df_prikaz.empty:
        st.info(f"Nema reči na spisku '{status_filter}'.")
    else:
        opcije_reci = {
            f"[{row['Lekcija']}. lekcija] {row['Reč (lema, sa članom)']} - {row['Prevod na srpski']}": idx
            for idx, row in df_prikaz.iterrows()
        }
        
        izabrana_labela = st.selectbox("Izaberite reč za promenu statusa:", list(opcije_reci.keys()))
        target_idx = opcije_reci[izabrana_labela]
        rec_naziv = st.session_state.df.loc[target_idx, 'Reč (lema, sa članom)']
        
        st.write(f"Prebaciti reč **'{rec_naziv}'** u **{novi_status}**?")
        potvrda = st.checkbox("Da, sigurna sam da želim da promenim status")
        
        if st.button(f"Promeni status u '{novi_status}'", type="primary", disabled=not potvrda):
            st.session_state.df.at[target_idx, 'Savladano/Nesavladano'] = novi_status
            st.success(f"Status za '{rec_naziv}' je uspešno promenjen u '{novi_status}'!")
            st.rerun()