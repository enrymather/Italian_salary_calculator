import streamlit as st
import numpy as np
import plotly.graph_objects as go


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="Calcolatore RAL → Netto",
    layout="wide"
)


# ------------------------------------------------------------
# STYLE (BIGGER FONTS + CLEANER LOOK)
# ------------------------------------------------------------

st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 21px;
}

h1 {
    font-size: 40px !important;
    font-weight: 700;
}

h2 {
    font-size: 32px !important;
}

h3 {
    font-size: 27px !important;
}

[data-testid="stMetricValue"] {
    font-size: 34px;
}

.section-divider {
    margin-top: 50px;
    margin-bottom: 20px;
}

.par-divider {
    margin-top: 10px;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# FORMAT FUNCTIONS
# ------------------------------------------------------------

def euro_format(value, decimals=2):
    formatted = f"{value:,.{decimals}f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted} €"


def euro_format_int(value):
    formatted = f"{int(round(value)):,}"
    formatted = formatted.replace(",", ".")
    return f"{formatted} €"


def percent_format(value):
    return f"{value:.1f}%"


def parse_percentage_input(value_str):
    if not value_str:
        return None

    try:
        cleaned = value_str.replace("%", "").replace(",", ".").strip()
        return float(cleaned) / 100
    except:
        return None


def info_box(text, background_color, font_size):
    return f"""
    <div style="
        background-color:{background_color};
        padding:12px 16px;
        border-left:4px solid #4a4943;
        border-radius:8px;
        font-size:{font_size}px;
        color:#000000;
        margin-top:10px;
        margin-bottom:10px;
    ">
    {text}
    </div>
    """


# ------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------

REGIONI = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia",
    "Toscana", "Trentino-Alto Adige (Bolzano)",
    "Trentino-Alto Adige (Trento)", "Umbria", "Valle d'Aosta", "Veneto"
]

IRPEF_BRACKETS = [
    (28000, 0.23),
    (50000, 0.33),
    (np.inf, 0.43)
]

DEFAULT_ADDIZ_REGIONALE = 0.02
DEFAULT_ADDIZ_COMUNALE = 0.008

MIN_RAL = 5000
MAX_RAL = 100000

SALARY_COMPONENTS = {"Netto": {"label": "netto_annuo", "color": "#10B981"},  # emerald green
                    "Contributi": {"label": "contributi", "color": "#FDBA74"},  # light orange
                    "IRPEF": {"label": "irpef_totale", "color": "#F87171"}  # light red
                    }


# ------------------------------------------------------------
# TAX FUNCTIONS
# ------------------------------------------------------------

def calcola_contributi(RAL, azienda_grande):
    aliquota = 0.0949 if azienda_grande else 0.0919
    return RAL * aliquota, aliquota


def calcola_irpef_lorda(imponibile):
    irpef = 0
    precedente = 0

    for limite, aliquota in IRPEF_BRACKETS:
        if imponibile > limite:
            irpef += (limite - precedente) * aliquota
            precedente = limite
        else:
            irpef += (imponibile - precedente) * aliquota
            break

    return irpef


def calcola_detrazione_lavoro_dipendente(imponibile):
    # source: https://www.randstad.it/blog-e-news/diritti-dei-lavoratori/calcolo-detrazioni-lavoro-dipendente/
    if imponibile <= 15000:
        return 1955
    elif imponibile <= 28000:
        return 1910 + 1190 * (28000 - imponibile) / 13000
    elif imponibile <= 50000:
        return 1910 * (50000 - imponibile) / 22000
    else:
        return 0


def calcola_ulteriore_detrazione(reddito):
    # source: https://www.randstad.it/blog-e-news/diritti-dei-lavoratori/calcolo-detrazioni-lavoro-dipendente/
    if 20000 < reddito <= 32000:
        return 1000
    elif 32000 < reddito < 40000:
        return 1000 * (40000 - reddito) / 8000
    else:
        return 0


def calcola_bonus_cuneo_fiscale(RAL):
    # source: https://www.coverflex.com/it/blog/taglio-cuneo-fiscale
    if RAL <= 8500:
        return RAL*0.071
    elif 8500 < RAL <= 15000:
        return RAL*0.053
    elif 15000 < RAL < 20000:
        return RAL*0.048
    else:
        return 0


def calcola_netto(RAL, azienda_grande, addiz_regionale_rate, addiz_comunale_rate, beneficio_fiscale_rate):
    contributi, aliquota_contr = calcola_contributi(RAL, azienda_grande)
    imponibile_irpef = (1 - beneficio_fiscale_rate) * (RAL - contributi)

    irpef_lorda = calcola_irpef_lorda(imponibile_irpef)
    detrazione_base = calcola_detrazione_lavoro_dipendente(imponibile_irpef)
    ulteriore_detrazione = calcola_ulteriore_detrazione(RAL)
    detrazione_totale = detrazione_base + ulteriore_detrazione
    bonus_cuneo_fiscale = calcola_bonus_cuneo_fiscale(RAL)

    irpef_netta = max(irpef_lorda - detrazione_totale, 0)

    addizionale_regionale = imponibile_irpef * addiz_regionale_rate
    addizionale_comunale = imponibile_irpef * addiz_comunale_rate

    irpef_totale = irpef_netta + addizionale_regionale + addizionale_comunale

    trattenute_totali = contributi + irpef_totale
    netto_annuo = RAL - trattenute_totali + bonus_cuneo_fiscale

    return {
        "netto_annuo": netto_annuo,
        "contributi": contributi,
        "aliquota_contr": aliquota_contr,
        "imponibile_irpef": imponibile_irpef,
        "irpef_lorda": irpef_lorda,
        "detrazione_base": detrazione_base,
        "ulteriore_detrazione": ulteriore_detrazione,
        "detrazione_totale": detrazione_totale,
        "bonus_cuneo_fiscale": bonus_cuneo_fiscale,
        "irpef_netta": irpef_netta,
        "addizionale_regionale": addizionale_regionale,
        "addizionale_comunale": addizionale_comunale,
        "irpef_totale": irpef_totale,
        "trattenute_totali": trattenute_totali
    }


# ------------------------------------------------------------
# UI
# ------------------------------------------------------------

st.title("Calcolatore RAL → Reddito Netto")

col1, col2 = st.columns(2)

with col1:
    RAL_input = st.number_input("RAL [€]", min_value=MIN_RAL, max_value=MAX_RAL, step=1000, value=30000)
    regione = st.selectbox("Regione di residenza", REGIONI)
    addiz_regionale_input = st.text_input("Addizionale regionale (%)", placeholder=str(100*DEFAULT_ADDIZ_REGIONALE).replace(".",","))
    perc_beneficio_fiscale = st.text_input("Perc. imponibile esente IRPEF (%)", placeholder="0")

with col2:
    mensilita = st.selectbox("Numero mensilità", [12, 13, 14])
    dimensione = st.selectbox("Dimensione azienda", ["< 15 dipendenti", "≥ 15 dipendenti"])
    addiz_comunale_input = st.text_input("Addizionale comunale (%)", placeholder=str(100*DEFAULT_ADDIZ_COMUNALE).replace(".",","))
    beneficio_fiscale_expl = st.markdown(
        info_box("N.B. La percentuale dell'imponibile IRPEF esente da tassazione è dovuta di solito all'applicazione di speciali regimi fiscali, come quello per lavoratori impatriati (c.d. del rientro dei cervelli).", "#78d2ff", 16),
        unsafe_allow_html=True
    )

addiz_regionale_rate = parse_percentage_input(addiz_regionale_input)
addiz_comunale_rate = parse_percentage_input(addiz_comunale_input)
beneficio_fiscale_rate = parse_percentage_input(perc_beneficio_fiscale)

if addiz_regionale_rate is None:
    addiz_regionale_rate = DEFAULT_ADDIZ_REGIONALE

if addiz_comunale_rate is None:
    addiz_comunale_rate = DEFAULT_ADDIZ_COMUNALE

if beneficio_fiscale_rate is None:
    beneficio_fiscale_rate = 0

if beneficio_fiscale_rate < 0:
    beneficio_fiscale_rate = 0
elif beneficio_fiscale_rate > 1:
    beneficio_fiscale_rate = 0.5

azienda_grande = dimensione == "≥ 15 dipendenti"

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# SLIDER (DRIVES EVERYTHING)
# ------------------------------------------------------------

RAL = st.slider(
    "Cambia RAL al volo:",
    min_value=MIN_RAL,
    max_value=MAX_RAL,
    step=1000,
    value=RAL_input,
    format="%d €"
)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# RE-COMPUTE RESULTS BASED ON SLIDER
# ------------------------------------------------------------

results = calcola_netto(RAL, azienda_grande, addiz_regionale_rate, addiz_comunale_rate, beneficio_fiscale_rate)
netto_annuo = results["netto_annuo"]
netto_mensile = netto_annuo / mensilita


# ------------------------------------------------------------
# MAIN METRICS
# ------------------------------------------------------------

colA, colB = st.columns(2)

with colA:
    st.markdown("### Reddito netto per mensilità")
    st.markdown(f"<div style='font-size:34px; margin-top:-10px'>{euro_format(netto_mensile)}</div>", unsafe_allow_html=True)

with colB:
    st.markdown("### Reddito netto annuale")
    st.markdown(f"<div style='font-size:34px; margin-top:-10px'>{euro_format(netto_annuo)}</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# DETAILS + PIE CHART SIDE-BY-SIDE
# ------------------------------------------------------------

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

col_det, col_pie = st.columns([1, 1])  # 50% / 50% split

with col_det:
    st.subheader("Dettaglio calcolo")

    st.write(f"**RAL:** {euro_format_int(RAL)}")
    st.write(f"**Contributi ({results['aliquota_contr']*100:.2f}%):** {euro_format_int(results['contributi'])}")
    st.write(f"**Imponibile IRPEF:** {euro_format_int(results['imponibile_irpef'])}")
    st.write(f"**IRPEF lorda:** {euro_format_int(results['irpef_lorda'])}")
    st.write(f"**Detrazione totale:** {euro_format_int(results['detrazione_totale'])} ({euro_format_int(results['detrazione_base'])} detrazione base + {euro_format_int(results['ulteriore_detrazione'])} ulteriore detrazione)")
    st.write(f"**Bonus cuneo fiscale:** {euro_format_int(results['bonus_cuneo_fiscale'])}")
    st.write(f"**IRPEF netta:** {euro_format_int(results['irpef_netta'])}")
    st.write(f"**Addizionale regionale:** {euro_format_int(results['addizionale_regionale'])}")
    st.write(f"**Addizionale comunale:** {euro_format_int(results['addizionale_comunale'])}")
    st.write(f"**IRPEF totale:** {euro_format_int(results['irpef_totale'])}")
    st.write(f"**Trattenute totali:** {euro_format_int(results['trattenute_totali'])} "
             f"({percent_format(results['trattenute_totali']/RAL*100)} sulla RAL)")
    st.write(f"**Stipendio annuale netto:** {euro_format_int(netto_annuo)}")

with col_pie:
    st.subheader("Composizione della RAL")
    
    mostra_mensili = st.toggle("Mostra valori mensili nel grafico a torta")
    divisor = mensilita if mostra_mensili else 1
    
    values = [results[v["label"]] for v in SALARY_COMPONENTS.values()]
    values_div = [v / divisor for v in values]
    percentages = [v / RAL * 100 for v in values]

    fig_pie = go.Figure(data=[go.Pie(
        labels=[k for k in SALARY_COMPONENTS.keys()],
        values=values_div,
        marker={"colors": [v["color"] for v in SALARY_COMPONENTS.values()]},
        text=[
            f"{euro_format_int(v)}<br>{percent_format(p)}"
            for v, p in zip(values_div, percentages)
        ],
        textinfo="text",
        hoverinfo="skip",
        sort=False
    )])

    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown(
        info_box("N.B. In caso si abbia più di un datore di lavoro nell'anno in corso, usare come valore di RAL quello complessivo: i risultati qui mostrati equivalgono a quelli che si avrebbero con la stessa RAL pagata da un unico datore (quindi a valle dei conguagli e della dichiarazione dei redditi).", "#cdff78", 16),
        unsafe_allow_html=True
    )

st.markdown('<div class="par-divider"></div>', unsafe_allow_html=True)

st.markdown(
    info_box("SEMPLIFICAZIONI ADOTTATE: <br>Le addizionali comunali e regionali possono differire sia per aliquote di reddito che per la situazione familiare del contribuente; quelle \"secche\" qui usate sono una semplificazione. <br>Anche la scelta della regione di residenza è stata inclusa per completezza, ma al momento non ha effetto sul risultato. <br>Quale ulteriore semplificazione non è stata introdotta la scelta del tipo di contratto (determinato, indeterminato, ecc.).", "#fff4ba", 18),
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# STACKED BAR CHART
# ------------------------------------------------------------

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.subheader("Evoluzione al variare della RAL")

RAL_range = np.arange(MIN_RAL, MAX_RAL+1, 2500)

fig = go.Figure()

for componente in SALARY_COMPONENTS.keys():
    y_vals = []
    perc_vals = []

    for r in RAL_range:
        res = calcola_netto(r, azienda_grande, addiz_regionale_rate, addiz_comunale_rate, beneficio_fiscale_rate)
        val = res[SALARY_COMPONENTS[componente]["label"]]

        y_vals.append(val)
        perc_vals.append(val / r * 100)

    fig.add_bar(
        x=RAL_range,
        y=y_vals,
        name=componente,
        marker_color=SALARY_COMPONENTS[componente]["color"],
        hovertemplate=[
            f"{euro_format_int(v)}<br>{percent_format(p)}"
            for v, p in zip(y_vals, perc_vals)
        ]
    )

fig.update_layout(
    barmode="stack",
    legend_title="Componente",
    yaxis_title="",

    xaxis=dict(
        tickvals=RAL_range,
        ticktext=[f"{int(x):,}".replace(",", ".") + " €" for x in RAL_range],
        tickangle=-40
    ),

    yaxis=dict(
        tickvals=np.linspace(0, max(RAL_range), 6),
        ticktext=[
            f"{int(y):,}".replace(",", ".") + " €"
            for y in np.linspace(0, max(RAL_range), 6)
        ]
    )
)

st.plotly_chart(fig, use_container_width=True)


