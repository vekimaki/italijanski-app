Naravno, evo celog koda sa ubačenim stilom za mnogo krupnija slova u bočnom meniju!

Samo iskopiraj ovo u svoj app.py na GitHub-u i meni će na telefonu odmah postati čitljiviji:

Python
import streamlit as st
import pandas as pd
import random

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None

# Link do tvoje Google Sheets tabele
SHEET_ID = "1mzbSkLBLwW9hCN6KSdWiLvYYiaaHoVtXV1xAkXI95XA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

KOLONA_STATUS = "Savladano/Nesavladano"
LIST_PODESAVANJA = "Podesavanja"

st.set_page_config(page_title="Učenje Italijanskog", page_icon="🇮🇹", layout="centered")

# CSS za boje i VEĆA SLOVA u meniju
st.markdown("""
<style>
    /* --- Povećanje slova u bočnom meniju (naslov i stavke) --- */
    section[data-testid="stSidebar"] h1 {
        font-size: 32px !important;
    }
    section[data-testid="stSidebar"] .stRadio p {
        font-size: 22px !important;
        font-weight: 600 !important;
        line-height: 2 !important;
    }
    
    /* 1. Velika zelena kartica sa rečju (samo za postavljanje pitanja) */
    .st-key-card_btn button {
        background-color: #2e7d32 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 25px !important;
        min-height: 160px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }
    .st-key-card_btn button:hover,
    .st-key-card_btn button:focus,
    .st-key-card_btn button:active {
        background-color: #1b5e20 !important;
        border: none !important;
        color: white !important;
    }
    .st-key-card_btn button p {
        color: white !important;
        font-size: 24px !important;
        font-weight: bold !important;
        line-height: 1.5 !important;
    }

    /* 2. Dugme ✓ Savladana (zeleno) */
    .st-key-btn_savladana button {
        background-color: #2e7d32 !important;
        border: none !important;
    }
    .st-key-btn_savladana button p {
        color: white !important;
        font-weight: bold !important;
    }

    /* 3. Dugme ✗ Nesavladana (crveno) */
    .st-key-btn_nesavladana button {
        background-color: #c62828 !important;
        border: none !important;
    }
    .st-key-btn_nesavladana button p {
        color: white !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Funkcije za trajno čuvanje
# ---------------------------------------------------------------------------
def cuvanje_ukljuceno():
    if gspread is None:
        return False
    try:
        return "gcp_service_account" in st.secrets
    except Exception:
        return False

CUVANJE = cuvanje_ukljuceno()

@st.cache_resource
def otvori_tabelu():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return gspread.authorize(creds).open_by_key(SHEET_ID)

def list_podesavanja():
    tabela = otvori_tabelu()
    try:
        return tabela.worksheet(LIST_PODESAVANJA)
    except gspread.WorksheetNotFound:
        ws = tabela.add_worksheet(title=LIST_PODESAVANJA, rows=5, cols=2)
        ws.update_cell(1, 1, "lekcije")
        return ws

def snimi_status(idx, status):
    if not CUVANJE:
        return
    try:
        ws = otvori_tabelu().sheet1
        if "kolona_statusa" not in st.session_state:
            zaglavlje = ws.row_values(1)
            if KOLONA_STATUS not in zaglavlje:
                zaglavlje.append(KOLONA_STATUS)
                ws.update_cell(1, len(zaglavlje), KOLONA_STATUS)
            st.session_state.kolona_statusa = zaglavlje.index(KOLONA_STATUS) + 1
        ws.update_cell(int(idx) + 2, st.session_state.kolona_statusa, status)
    except Exception as e:
        st.warning(f"Status nije sačuvan u tabeli: {e}")

def snimi_izbor_lekcija(lekcije):
    if not CUVANJE:
        return
    try:
        list_podesavanja().update_cell(1, 2, ";".join(str(l) for l in lekcije))
    except Exception as e:
        st.warning(f"Izbor lekcija nije sačuvan u tabeli: {e}")

def _u_lekciju(x):
    x = x.strip()
    return int(x) if x.isdigit() else x

def ucitaj_izbor_lekcija(sve_lekcije):
    sacuvane = []
    if CUVANJE:
        try:
            vrednost = list_podesavanja().cell(1, 2).value or ""
            sacuvane = [_u_lekciju(x) for x in vrednost.split(";") if x.strip()]
        except Exception:
            sacuvane = []
    if not sacuvane and "lekcije" in st.query_params:
        sacuvane = [_u_lekciju(x) for x in st.query_params["lekcije"].split(",") if x.strip()]
    izabrane = [l for l in sacuvane if l in sve_lekcije]
    return izabrane or sve_lekcije

# ---------------------------------------------------------------------------
# Učitavanje podataka
# ---------------------------------------------------------------------------
@st.cache_data(ttl=2)
def ucitaj_podatke():
    try:
        df = pd.read_csv(SHEET_URL)
        if KOLONA_STATUS not in df.columns:
            df[KOLONA_STATUS] = 'Nesavladano'
        else:
            df[KOLONA_STATUS] = df[KOLONA_STATUS].fillna('Nesavladano')
        return df
    except Exception as e:
        st.error(f"Greška pri učitavanju tabele: {e}")
        return pd.DataFrame()

# Inicijalizacija podataka
if "df" not in st.session_state:
    st.session_state.df = ucitaj_podatke()

sve_lekcije_list = sorted(st.session_state.df['Lekcija'].unique().tolist()) if not st.session_state.df.empty else []

if "izabrane_lekcije" not in st.session_state:
    st.session_state.izabrane_lekcije = ucitaj_izbor_lekcija(sve_lekcije_list)

if "prikazi_prevod" not in st.session_state:
    st.session_state.prikazi_prevod = False

if "trenutna_rec" not in st.session_state:
    st.session_state.trenutna_rec = None

# Meni za navigaciju
st.sidebar.title("🇮🇹 Meni")
izbor_menija = st.sidebar.radio("Izaberite opciju:", ["▶ Provera znanja", "📚 Izbor lekcija", "📋 Pregled reči"])
if not CUVANJE:
    st.sidebar.caption("⚠️ Trajno čuvanje nije podešeno: izbor lekcija i savladane reči se brišu kad zatvoriš aplikaciju.")

# --- 1. PROVERA ZNANJA ---
if izbor_menija == "▶ Provera znanja":
    st.title("🇮🇹 Provera znanja")

    df = st.session_state.df
    izabrane = st.session_state.izabrane_lekcije

    filtrirano = df[(df['Lekcija'].isin(izabrane)) & (df[KOLONA_STATUS] == 'Nesavladano')]

    if filtrirano.empty:
        st.success("🎉 Bravo! Prešli ste sve nesavladane reči iz izabranih lekcija!")
    else:
        sledeca = st.button("🔄 Sledeća reč")
        if st.session_state.trenutna_rec is None or sledeca:
            st.session_state.prikazi_prevod = False
            slucajni_idx = random.choice(filtrirano.index.tolist())
            st.session_state.trenutna_rec = filtrirano.loc[slucajni_idx]
            st.session_state.trenutni_idx = slucajni_idx
            st.session_state.smer = random.choice(['IT_SRB', 'SRB_IT'])

        rec_podaci = st.session_state.trenutna_rec
        smer = st.session_state.smer

        italijanski = rec_podaci['Reč (lema, sa članom)']
        srpski = rec_podaci['Prevod na srpski']

        if smer == 'IT_SRB':
            prikaz_rec = italijanski
            jezik = "Italijanski"
        else:
            prikaz_rec = srpski
            jezik = "Srpski"

        st.caption(f"Reč na jeziku: **{jezik}**")

        # Ako prevod još nije prikazan -> Zeleno dugme-kartica
        if not st.session_state.prikazi_prevod:
            labela = f"🗣️ {prikaz_rec}\n\n(klikni na karticu za prevod)"
            if st.button(labela, use_container_width=True, key="card_btn"):
                st.session_state.prikazi_prevod = True
                st.rerun()
        # Ako je kliknuto -> Sistematska neutralna kartica sa prevodom i detaljima
        else:
            st.info(
                f"🇮🇹 **Italijanski:** {italijanski}\n\n"
                f"🇷🇸 **Prevod:** {srpski}\n\n"
                f"📌 **Vrsta:** {rec_podaci['Vrsta reči']} | 📖 **Lekcija:** {rec_podaci['Lekcija']}"
            )

        if st.session_state.prikazi_prevod:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Savladana", use_container_width=True, key="btn_savladana"):
                    st.session_state.df.at[st.session_state.trenutni_idx, KOLONA_STATUS] = 'Savladano'
                    snimi_status(st.session_state.trenutni_idx, 'Savladano')
                    st.session_state.trenutna_rec = None
                    st.session_state.prikazi_prevod = False
                    st.rerun()
            with col2:
                if st.button("✗ Nesavladana", use_container_width=True, key="btn_nesavladana"):
                    st.session_state.trenutna_rec = None
                    st.session_state.prikazi_prevod = False
                    st.rerun()

# --- 2. IZBOR LEKCIJA ---
elif izbor_menija == "📚 Izbor lekcija":
    st.title("📚 Izbor lekcija za proveru")

    izabrane_temp = st.multiselect(
        "Izaberite lekcije koje želite da učite:",
        options=sve_lekcije_list,
        default=st.session_state.izabrane_lekcije
    )

    if st.button("Sačuvaj izbor", type="primary"):
        if not izabrane_temp:
            st.warning("Morate izabrati makar jednu lekciju!")
        else:
            st.session_state.izabrane_lekcije = izabrane_temp
            st.session_state.trenutna_rec = None
            st.session_state.prikazi_prevod = False
            st.query_params["lekcije"] = ",".join(map(str, izabrane_temp))
            snimi_izbor_lekcija(izabrane_temp)
            if CUVANJE:
                st.success("Izbor lekcija je trajno sačuvan.")
            else:
                st.success("Izbor lekcija je sačuvan samo u ovom linku (trajno čuvanje nije podešeno).")

# --- 3. PREGLED REČI ---
elif izbor_menija == "📋 Pregled reči":
    st.title("📋 Pregled reči")

    status_filter = st.radio("Prikaži:", ["Savladane", "Nesavladane"], horizontal=True)
    izabrani_status = "Savladano" if status_filter == "Savladane" else "Nesavladano"
    novi_status = "Nesavladano" if izabrani_status == "Savladano" else "Savladano"

    df_prikaz = st.session_state.df[st.session_state.df[KOLONA_STATUS] == izabrani_status]

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
            st.session_state.df.at[target_idx, KOLONA_STATUS] = novi_status
            snimi_status(target_idx, novi_status)
            st.session_state.trenutna_rec = None
            st.success(f"Status za '{rec_naziv}' je uspešno promenjen u '{novi_status}'!")
            st.rerun()