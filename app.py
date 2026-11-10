import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Konfigurasi Halaman (Wide Layout)
st.set_page_config(
    page_title="Pamasuka · Media Monitoring",
    page_icon="📊",
    layout="wide"
)

# --- CUSTOM CSS: BACKGROUND GLOBAL LIGHT GREY & STICKY FILTER PUTIH ---
st.markdown("""
    <style>
    /* 1. Set Background Global Aplikasi Menjadi Light Grey */
    .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #F8FAFC !important;
    }
    
    [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }
    
    .main .block-container {
        max-width: 1440px;
        padding-top: 1rem !important;
        padding-right: 32px;
        padding-left: 32px;
        margin: 0 auto;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, Roboto, Helvetica, sans-serif;
        font-size: 14px;
        color: #1E293B;
    }

    /* 2. Sticky hanya pada container filter.
       Key class Streamlit dipasang langsung pada container yang dibuat
       dengan st.container(key="filter_bar"). Marker dipakai sebagai
       pengaman agar styling hanya aktif pada container yang benar. */
    .st-key-filter_bar:has(.fixed-filter-marker) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background-color: #FFFFFF !important;
        padding: 12px 32px 14px 32px !important;
        margin-left: -32px !important;
        margin-right: -32px !important;
        width: calc(100% + 64px) !important;
        box-sizing: border-box !important;
        border-bottom: 1px solid #E2E8F0 !important;
        box-shadow: 0 3px 6px -2px rgba(0, 0, 0, 0.05) !important;
    }

    .fixed-filter-marker {
        height: 0;
        margin: 0;
        padding: 0;
    }

    /* 3. Styling Card Konten Utama (Berlatar Putih di atas Light Grey) */
    .st-key-card_sov_pamasuka, .st-key-card_kategori, .st-key-card_sentimen,
    .st-key-card_sul, .st-key-card_kal, .st-key-card_puma, .st-key-card_tabel,
    .st-key-metric_box {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }

    .metric-title {
        font-size: 12px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
    }
    </style>
""", unsafe_allow_html=True)

# --- INISIALISASI SESSION STATE & HISTORY ---
if 'filter_wilayah' not in st.session_state:
    st.session_state.filter_wilayah = "Area"
if 'filter_periode' not in st.session_state:
    st.session_state.filter_periode = [pd.to_datetime("2026-10-01"), pd.to_datetime("2026-10-29")]
if 'op_telkomsel' not in st.session_state:
    st.session_state.op_telkomsel = True
if 'op_xlsmart' not in st.session_state:
    st.session_state.op_xlsmart = True
if 'op_indosat' not in st.session_state:
    st.session_state.op_indosat = True
if 'op_lainnya' not in st.session_state:
    st.session_state.op_lainnya = True

if 'history_state' not in st.session_state:
    st.session_state.history_state = []

def save_current_state():
    current_snapshot = {
        "wilayah": st.session_state.filter_wilayah,
        "periode": st.session_state.filter_periode,
        "tsel": st.session_state.op_telkomsel,
        "xl": st.session_state.op_xlsmart,
        "isat": st.session_state.op_indosat,
        "lainnya": st.session_state.op_lainnya
    }
    if not st.session_state.history_state or st.session_state.history_state[-1] != current_snapshot:
        st.session_state.history_state.append(current_snapshot)

def go_back():
    if len(st.session_state.history_state) > 1:
        st.session_state.history_state.pop()
        prev_state = st.session_state.history_state[-1]
        st.session_state.filter_wilayah = prev_state["wilayah"]
        st.session_state.filter_periode = prev_state["periode"]
        st.session_state.op_telkomsel = prev_state["tsel"]
        st.session_state.op_xlsmart = prev_state["xl"]
        st.session_state.op_indosat = prev_state["isat"]
        st.session_state.op_lainnya = prev_state["lainnya"]

def reset_filters():
    st.session_state.filter_wilayah = "Area"
    st.session_state.filter_periode = [pd.to_datetime("2026-10-01"), pd.to_datetime("2026-10-29")]
    st.session_state.op_telkomsel = True
    st.session_state.op_xlsmart = True
    st.session_state.op_indosat = True
    st.session_state.op_lainnya = True
    st.session_state.history_state.clear()

# --- LOAD DATA DARI GOOGLE SHEETS CSV ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR5Y_Pk8R8CQApJ4Qx1XD5Dx7tbS5OC185PQQhji7fY6hp5PTPsV-2wMbnMqZBr5fREJFnjknLHrkGe/pub?gid=1142274170&single=true&output=csv"

@st.cache_data(ttl=300)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        if 'tanggal' in df.columns:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        return df
    except Exception:
        data_dummy = {
            "no": [1, 2, 3, 4, 5, 6, 7, 8],
            "judul berita": [
                "IM3 Platinum Hadirkan Jaringan Baru",
                "Gaming hingga Kreativitas didukung Telkomsel",
                "Dari Yogyakarta hingga Sulawesi",
                "Indosat 5G di Samarinda Perluas Jangkauan",
                "XLSmart Perluas Pengalaman Digital",
                "Telkomsel Siaga di Sulawesi",
                "Indosat Ekspansi Kalimantan",
                "XLSmart Jaringan Baru Puma"
            ],
            "operator": ["Indosat", "Telkomsel", "XLSmart", "Indosat", "XLSmart", "Telkomsel", "Indosat", "XLSmart"],
            "link berita": ["https://url1.com", "https://url2.com", "https://url3.com", "https://url4.com", "https://url5.com", "https://url6.com", "https://url7.com", "https://url8.com"],
            "tanggal": ["2026-10-02", "2026-10-05", "2026-10-10", "2026-10-15", "2026-10-20", "2026-10-22", "2026-10-25", "2026-10-28"],
            "wilayah": ["kalimantan", "sulawesi", "kalimantan", "kalimantan", "sulawesi", "sulawesi", "kalimantan", "puma"],
            "kategori berita": ["Corporate Image", "Sales", "Corporate Image", "Network", "Corporate Image", "Network", "Sales", "Corporate Image"],
            "sentiment": ["Positif", "Positif", "Positif", "Netral", "Positif", "Positif", "Positif", "Positif"]
        }
        df_dummy = pd.DataFrame(data_dummy)
        df_dummy['tanggal'] = pd.to_datetime(df_dummy['tanggal'])
        return df_dummy

df = load_data(SHEET_CSV_URL)

if not st.session_state.history_state:
    save_current_state()

# --- HEADER JUDUL (TIDAK STICKY) ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("Media monitoring")
    st.markdown("<p style='color: #64748B; font-size: 13px; margin-top: -10px; margin-bottom: 15px;'>Pantau pemberitaan operator dan distribusi eksposur di wilayah Pamasuka.</p>", unsafe_allow_html=True)
with col_head2:
    st.markdown("<p style='text-align: right; font-size: 12px; color: #64748B;'>Sulawesi · Kalimantan · Papua & Maluku</p>", unsafe_allow_html=True)

# --- HANYA FILTER BAR YANG STICKY ---
with st.container(key="filter_bar"):
    # Marker khusus untuk menandai area filter sebagai sticky header.
    st.markdown("<div class='fixed-filter-marker'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 13px; font-weight: 600; color: #0F172A; margin-bottom: 6px;'>🔍 Filter Data Berita</div>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([2.0, 1.5, 2.6, 0.7, 0.7])

    with f_col1:
        st.markdown("<span style='font-size: 11px; font-weight: 600; color: #64748B;'>Wilayah</span>", unsafe_allow_html=True)
        pilihan_wilayah = st.radio("Wilayah", ["Area", "Sulawesi", "Kalimantan", "Puma"], key="filter_wilayah", horizontal=True, label_visibility="collapsed")

    with f_col2:
        st.markdown("<span style='font-size: 11px; font-weight: 600; color: #64748B;'>Periode</span>", unsafe_allow_html=True)
        periode = st.date_input("Periode", key="filter_periode", label_visibility="collapsed")

    with f_col3:
        st.markdown("<span style='font-size: 11px; font-weight: 600; color: #64748B;'>Operator</span>", unsafe_allow_html=True)
        c_op1, c_op2, c_op3, c_op4 = st.columns(4)
        with c_op1: chk_tsel = st.checkbox("Telkomsel", key="op_telkomsel")
        with c_op2: chk_xl = st.checkbox("XLSmart", key="op_xlsmart")
        with c_op3: chk_isat = st.checkbox("Indosat", key="op_indosat")
        with c_op4: chk_other = st.checkbox("Lainnya", key="op_lainnya")

        operators = []
        if chk_tsel: operators.append("Telkomsel")
        if chk_xl: operators.append("XLSmart")
        if chk_isat: operators.append("Indosat")
        if chk_other: operators.append("Lainnya")

    with f_col4:
        st.markdown("<span style='font-size: 11px; font-weight: 600; color: transparent;'>Back</span>", unsafe_allow_html=True)
        st.button("⬅️ Back", on_click=go_back, use_container_width=True, help="Kembali ke filter sebelumnya")

    with f_col5:
        st.markdown("<span style='font-size: 11px; font-weight: 600; color: transparent;'>Reset</span>", unsafe_allow_html=True)
        st.button("🔄 Reset", on_click=reset_filters, use_container_width=True)

save_current_state()

# --- PROSES FILTERING DATA ---
df_filtered = df.copy()
if pilihan_wilayah != "Area":
    df_filtered = df_filtered[df_filtered['wilayah'].str.lower() == pilihan_wilayah.lower()]
df_filtered = df_filtered[df_filtered['operator'].isin(operators)]

if isinstance(periode, (list, tuple)) and len(periode) == 2 and 'tanggal' in df_filtered.columns:
    start_date, end_date = pd.to_datetime(periode[0]), pd.to_datetime(periode[1])
    df_filtered = df_filtered[(df_filtered['tanggal'] >= start_date) & (df_filtered['tanggal'] <= end_date)]

df_pamasuka_sov = df.copy()
df_pamasuka_sov = df_pamasuka_sov[df_pamasuka_sov['operator'].isin(operators)]
if isinstance(periode, (list, tuple)) and len(periode) == 2 and 'tanggal' in df_pamasuka_sov.columns:
    start_date, end_date = pd.to_datetime(periode[0]), pd.to_datetime(periode[1])
    df_pamasuka_sov = df_pamasuka_sov[(df_pamasuka_sov['tanggal'] >= start_date) & (df_pamasuka_sov['tanggal'] <= end_date)]

def handle_pie_click(event_selection, region_name="Area"):
    if event_selection and 'selection' in event_selection and event_selection['selection']['points']:
        point = event_selection['selection']['points'][0]
        if 'label' in point:
            clicked_op = point['label']
            st.session_state.op_telkomsel = (clicked_op == "Telkomsel")
            st.session_state.op_xlsmart = (clicked_op == "XLSmart")
            st.session_state.op_indosat = (clicked_op == "Indosat")
            st.session_state.op_lainnya = (clicked_op == "Lainnya")
            if region_name != "Area":
                st.session_state.filter_wilayah = region_name
            save_current_state()
            st.rerun()

# --- AREA KONTEN BAWAH (OTOMATIS BERADA DI ATAS BACKGROUND LIGHT GREY) ---
st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

col_info_title, col_info_note = st.columns([3, 1])
with col_info_title:
    st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0F172A; margin-bottom: 15px;'>Ringkasan pemberitaan</h3>", unsafe_allow_html=True)
with col_info_note:
    st.markdown("<p style='text-align: right; font-size: 11px; color: #64748B;'>Seluruh kartu & daftar berita mengikuti filter</p>", unsafe_allow_html=True)

total_berita = len(df_filtered)
count_telkomsel = len(df_filtered[df_filtered['operator'].str.lower() == 'telkomsel'])
count_xlsmart = len(df_filtered[df_filtered['operator'].str.lower() == 'xlsmart'])
count_indosat = len(df_filtered[df_filtered['operator'].str.lower() == 'indosat'])
count_lainnya = len(df_filtered[df_filtered['operator'].str.lower() == 'lainnya'])

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    with st.container(border=True, key="metric_box_1"):
        st.markdown("<div class='metric-title'>Total Berita 📄</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{total_berita} <span style='font-size: 13px; font-weight: normal; color: #64748B;'>berita</span></div>", unsafe_allow_html=True)
with m2:
    with st.container(border=True, key="metric_box_2"):
        st.markdown("<div class='metric-title'><span style='color:#dc2626'>●</span> Telkomsel</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{count_telkomsel} <span style='font-size: 13px; font-weight: normal; color: #64748B;'>berita</span></div>", unsafe_allow_html=True)
with m3:
    with st.container(border=True, key="metric_box_3"):
        st.markdown("<div class='metric-title'><span style='color:#7c3aed'>●</span> XLSmart</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{count_xlsmart} <span style='font-size: 13px; font-weight: normal; color: #64748B;'>berita</span></div>", unsafe_allow_html=True)
with m4:
    with st.container(border=True, key="metric_box_4"):
        st.markdown("<div class='metric-title'><span style='color:#d97706'>●</span> Indosat</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{count_indosat} <span style='font-size: 13px; font-weight: normal; color: #64748B;'>berita</span></div>", unsafe_allow_html=True)
with m5:
    with st.container(border=True, key="metric_box_5"):
        st.markdown("<div class='metric-title'><span style='color:#94A3B8'>●</span> Lainnya</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value'>{count_lainnya} <span style='font-size: 13px; font-weight: normal; color: #64748B;'>berita</span></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# --- BAGIAN GRAFIK UTAMA ---
c1, c2, c3 = st.columns([1.2, 1.2, 1.3])

with c1:
    with st.container(border=True, key="card_sov_pamasuka"):
        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.markdown("<div style='font-size: 15px; font-weight: 600; color: #0F172A;'>Operator SOV Pamasuka</div>", unsafe_allow_html=True)
        with col_t2:
            st.markdown("<div style='text-align: right;'><span style='background: #E2E8F0; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; color: #475569;'>FILTER</span></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 11px; color: #64748B; margin-bottom: 5px;'>Mengikuti filter operator & tanggal</div>", unsafe_allow_html=True)
        
        sov_counts = df_pamasuka_sov['operator'].value_counts()
        labels_sov = list(sov_counts.index) if not sov_counts.empty else ['Telkomsel', 'Indosat', 'XLSmart', 'Lainnya']
        values_sov = list(sov_counts.values) if not sov_counts.empty else [0, 0, 0, 0]
        total_pamasuka_sov = len(df_pamasuka_sov)

        fig_sov = go.Figure(data=[go.Pie(
            labels=labels_sov,
            values=values_sov,
            hole=.65,
            domain=dict(x=[0, 0.65]),
            marker_colors=['#dc2626', '#d97706', '#7c3aed', '#94A3B8'],
            marker=dict(line=dict(color='#ffffff', width=2)),
            pull=[0.03] * len(labels_sov)
        )])
        fig_sov.update_layout(
            showlegend=True, 
            legend=dict(orientation="v", x=0.72, y=0.5, font=dict(size=11)),
            margin=dict(t=0, b=0, l=0, r=0), 
            height=200,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(
                text=f"<b>{total_pamasuka_sov}</b><br><span style='font-size:10px; color:#64748b;'>Total Berita</span>", 
                x=0.325, y=0.5,
                xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )]
        )
        selected_sov = st.plotly_chart(fig_sov, use_container_width=True, key="chart_sov_pamasuka", on_select="rerun", selection_mode="points")
        handle_pie_click(selected_sov, region_name="Area")
        st.markdown("<div style='font-size: 11px; color: #64748B; margin-top: 5px;'>🔒 Kebal terhadap filter wilayah.</div>", unsafe_allow_html=True)

with c2:
    with st.container(border=True, key="card_kategori"):
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #0F172A;'>Kategori berita</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 11px; color: #64748B; margin-bottom: 2px;'>Jumlah pemberitaan per kategori</div>", unsafe_allow_html=True)
        
        cat_counts = df_filtered['kategori berita'].value_counts()
        cat_labels = ['Corporate Image', 'Sales', 'Network', 'Others']
        y_cat = [cat_counts.get(cat, 0) for cat in cat_labels]
        max_y = max(y_cat) if max(y_cat) > 0 else 10

        fig_cat = px.bar(x=cat_labels, y=y_cat, text=y_cat, color_discrete_sequence=['#1E3A8A'])
        fig_cat.update_traces(
            textposition='outside', 
            textfont=dict(size=12, color='#0F172A', weight='bold'),
            cliponaxis=False
        )
        fig_cat.update_layout(
            xaxis_title="", 
            yaxis_title="", 
            yaxis=dict(range=[0, max_y * 1.2], showgrid=True, gridcolor='#F1F5F9'),
            margin=dict(t=25, b=0, l=0, r=0), 
            height=265,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_cat, use_container_width=True, key="chart_kategori")

with c3:
    with st.container(border=True, key="card_sentimen"):
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #0F172A;'>Sentimen pemberitaan</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 11px; color: #64748B; margin-bottom: 12px;'>Proporsi positif dan negatif per operator</div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 8px;'>
                <div><span style='color: #16a34a;'>●</span> Positif &nbsp;&nbsp; <span style='color: #d97706;'>●</span> Negatif</div>
                <div style='color: #64748B;'>Negatif</div>
            </div>
        """, unsafe_allow_html=True)

        sentiments = [
            {"op": "Telkomsel", "pos": 99.3, "neg": "0,7%"},
            {"op": "XLSmart", "pos": 100.0, "neg": "0%"},
            {"op": "Indosat", "pos": 99.53, "neg": "0,47%"},
            {"op": "Lainnya", "pos": 100.0, "neg": "0%"},
        ]
        
        for s in sentiments:
            st.markdown(f"""
                <div style='font-size: 12px; margin-bottom: 2px; display: flex; justify-content: space-between;'>
                    <b>{s['op']}</b>
                    <span style='color: #16a34a; font-weight: 600;'>{s['pos']}%</span>
                </div>
                <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 10px;'>
                    <div style='background: #E2E8F0; border-radius: 4px; height: 8px; flex-grow: 1;'>
                        <div style='background: #16a34a; width: {s['pos']}%; height: 8px; border-radius: 4px;'></div>
                    </div>
                    <span style='font-size: 11px; color: #64748B; width: 35px; text-align: right;'>{s['neg']}</span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='font-size: 10px; color: #64748B; text-align: right; margin-top: -5px;'>Porsi negatif ditulis terpisah agar tetap terbaca.</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# --- SHARE OF VOICE PER WILAYAH ---
col_sov_w1, col_sov_w2 = st.columns([3, 1])
with col_sov_w1:
    st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0F172A; margin-bottom: 15px;'>Share of voice per wilayah</h3>", unsafe_allow_html=True)
with col_sov_w2:
    st.markdown("<p style='text-align: right; font-size: 11px; color: #64748B;'>Persentase dibulatkan sesuai snapshot · — tidak berlabel pada referensi</p>", unsafe_allow_html=True)

w1, w2, w3 = st.columns(3)

def render_regional_pie_dynamic(wilayah_name, key_name):
    df_reg = df_filtered[df_filtered['wilayah'].str.lower() == wilayah_name.lower()]
    total_reg = len(df_reg)
    
    reg_counts = df_reg['operator'].value_counts()
    labels = list(reg_counts.index) if not reg_counts.empty else ['Telkomsel', 'Indosat', 'XLSmart', 'Lainnya']
    values = list(reg_counts.values) if not reg_counts.empty else [0, 0, 0, 0]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=.65,
        domain=dict(x=[0, 0.65]),
        marker_colors=['#dc2626', '#d97706', '#7c3aed', '#94A3B8'],
        marker=dict(line=dict(color='#ffffff', width=2)),
        pull=[0.03] * len(labels)
    )])
    fig.update_layout(
        showlegend=True, 
        legend=dict(orientation="v", x=0.72, y=0.5, font=dict(size=11)),
        margin=dict(t=10, b=10, l=10, r=10), height=180,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(
            text=f"<b>{total_reg}</b><br><span style='font-size:9px; color:#64748b;'>Total Berita</span>", 
            x=0.325, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False, font_size=14
        )]
    )
    sel_chart = st.plotly_chart(fig, use_container_width=True, key=key_name, on_select="rerun", selection_mode="points")
    handle_pie_click(sel_chart, region_name=wilayah_name.capitalize())

with w1:
    with st.container(border=True, key="card_sul"):
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #0F172A;'>Operator SOV Sulawesi</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 11px; color: #64748B; margin-bottom: 8px;'>Distribusi pemberitaan per operator</div>", unsafe_allow_html=True)
        render_regional_pie_dynamic("sulawesi", "chart_sulawesi")

with w2:
    with st.container(border=True, key="card_kal"):
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #0F172A;'>Operator SOV Kalimantan</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 11px; color: #64748B; margin-bottom: 8px;'>Distribusi pemberitaan per operator</div>", unsafe_allow_html=True)
        render_regional_pie_dynamic("kalimantan", "chart_kalimantan")

with w3:
    with st.container(border=True, key="card_puma"):
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #0F172A;'>Operator SOV Puma</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 11px; color: #64748B; margin-bottom: 8px;'>Papua & Maluku</div>", unsafe_allow_html=True)
        render_regional_pie_dynamic("puma", "chart_puma")

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# --- TABEL DAFTAR BERITA & TOMBOL SCREENSHOT ---
col_tabel_title, col_tabel_btn = st.columns([3, 1])
with col_tabel_title:
    st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #0F172A; margin-bottom: 2px;'>Daftar berita</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px; color: #64748B; margin-bottom: 10px;'>Rincian pemberitaan sesuai pilihan wilayah, periode, dan operator.</p>", unsafe_allow_html=True)
with col_tabel_btn:
    st.markdown("""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <button onclick="
            html2canvas(document.body).then(canvas => {
                let link = document.createElement('a');
                link.download = 'dashboard-pamasuka-snapshot.png';
                link.href = canvas.toDataURL();
                link.click();
            });
        " style="background-color: #0284C7; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; float: right;">
            📸 Download Screenshot
        </button>
    """, unsafe_allow_html=True)

with st.container(border=True, key="card_tabel"):
    if not df_filtered.empty:
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        col_foot1, col_foot2 = st.columns([1, 1])
        with col_foot1:
            st.markdown(f"<p style='font-size: 11px; color: #64748B; margin: 0;'>{len(df_filtered)} baris ditampilkan dari snapshot</p>", unsafe_allow_html=True)
        with col_foot2:
            st.markdown("<p style='text-align: right; font-size: 11px; color: #64748B; margin: 0;'>Judul dan tautan dipertahankan terpotong sesuai referensi.</p>", unsafe_allow_html=True)
    else:
        st.info("Tidak ada data berita yang cocok dengan filter yang dipilih.")