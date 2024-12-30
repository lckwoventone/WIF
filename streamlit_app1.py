import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime


# Funzione per calcolare la crescita dell'investimento
def calcola_crescita_investimento(ticker, start_date, end_date,
                                  investimento_iniziale):
    df = yf.download(ticker, start=start_date, end=end_date)
    df['Rendimento'] = df['Adj Close'].pct_change()
    df['Valore Investimento'] = investimento_iniziale * (
        1 + df['Rendimento']).cumprod()
    return df


# Funzione per calcolare il rendimento medio annuo in percentuale
def calcola_rendimento_medio_annuo(df):
    if df.empty:
        return None

    # Calcola il rendimento totale composto
    rendimento_totale = (df['Rendimento'] + 1).prod()

    # Calcola il numero di giorni di trading nel DataFrame
    numero_giorni = len(df)

    # Calcola il rendimento medio annuo
    rendimento_medio_annuo = rendimento_totale**(252 / numero_giorni) - 1

    # Converti in percentuale
    rendimento_medio_annuo_percentuale = rendimento_medio_annuo * 100

    return rendimento_medio_annuo_percentuale



# Funzione per calcolare la proiezione del valore di un investimento futuro
def calcola_proiezione_valore_futuro(valore_iniziale, rendimento_medio, anni):
    valore_futuro = valore_iniziale * (1 + rendimento_medio / 100)**anni
    return valore_futuro


# Funzione per ottenere i simboli delle azioni predefiniti
def get_default_stock_symbols():
    symbols = {
        "CSSPX.MI": "Vanguard S&P 500 UCITS ETF",
        "AGG": "iShares Core U.S. Aggregate Bond ETF",
        "SPY": "SPDR S&P 500 ETF Trust",
        "TLT": "iShares 20+ Year Treasury Bond ETF",
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc.",
        "AMZN": "Amazon.com Inc."
    }
    return symbols


# Funzione principale per eseguire l'app Streamlit
def run_streamlit_app():
    st.title("Simulatore di Crescita dell'Investimento")

    # Input dell'utente
    investimento_iniziale = st.number_input("Inserisci l'importo iniziale (€)",
                                            value=2000)

    # Ottieni i simboli delle azioni predefiniti
    stock_symbols = get_default_stock_symbols()
    descrizioni_predefinite = [
        f"{sym} - {desc}" for sym, desc in stock_symbols.items()
    ]

    # Casella di ricerca per i simboli delle azioni 
    search_query = st.text_input(
        "Cerca un prodotto finanziario (es. AAPL, GOOGL, etc.)")

    # Filtra le descrizioni predefinite in base alla query di ricerca
    filtered_descrizioni = [
        desc for desc in descrizioni_predefinite
        if search_query.upper() in desc
    ]

    # Se la ricerca non trova risultati nei simboli predefiniti, utilizza yfinance per cercare
    if not filtered_descrizioni and search_query:
        try:
            # Esegui una ricerca avanzata su yfinance
            result = yf.Ticker(search_query)
            if result.info:
                # Aggiungi il risultato della ricerca alla lista delle descrizioni filtrate
                symbol = result.info.get('symbol', search_query)
                description = result.info.get('longName',
                                              'No description available')
                filtered_descrizioni.append(f"{symbol} - {description}")
        except Exception as e:
            st.error(f"Errore durante la ricerca!: {e}")

    # Selectbox per i simboli delle azioni filtrati
    if filtered_descrizioni:
        prodotto_finanziario = st.selectbox(
            "Seleziona il prodotto finanziario", filtered_descrizioni)
        selected_symbol = prodotto_finanziario.split(" - ")[0]
    else:
        st.write("Nessun prodotto trovato.")
        return

    anni = st.slider("Seleziona lo span temporale (anni)",
                     min_value=1,
                     max_value=20,
                     value=10)

    # Calcolo delle date
    oggi = datetime.now()
    start_date = oggi.replace(year=oggi.year - anni).strftime('%Y-%m-%d')
    end_date = oggi.strftime('%Y-%m-%d')

    # Calcolo della crescita dell'investimento
    df = calcola_crescita_investimento(selected_symbol, start_date, end_date,
                                       investimento_iniziale)

    # Calcolo del rendimento medio annuo
    rendimento_medio_annuo = calcola_rendimento_medio_annuo(df)

    # Calcolo del valore attuale dell'investimento
    valore_attuale = df['Valore Investimento'].iloc[-1]

    # Calcolo della proiezione del valore di un investimento futuro
    valore_futuro = calcola_proiezione_valore_futuro(investimento_iniziale,
                                                     rendimento_medio_annuo,
                                                     anni)

    # Mostra i KPI in box colorati con stile personalizzato
    st.header("KPI")
    col1, col2, col3 = st.columns(3)
    kpi_style = """
    <style>
    .kpi-box {
        padding: 10px;
        border-radius: 10px;
        margin: 10px;
        text-align: center;
        font-size: 1.2em;
    }
    .kpi-value {
        font-weight: bold;
        font-size: 1.5em;
    }
    </style>
    """
    st.markdown(kpi_style, unsafe_allow_html=True)

    with col1:
        st.markdown(
            f'<div class="kpi-box" style="background-color: #D6EAF8;"><div>Rendimento Medio Annuo</div><div class="kpi-value">{rendimento_medio_annuo:.2f}%</div></div>',
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div class="kpi-box" style="background-color: #D5F5E3;"><div>Valore Attuale dell\'Investimento</div><div class="kpi-value">€ {valore_attuale:.2f}</div></div>',
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            f'<div class="kpi-box" style="background-color: #FCF3CF;"><div>Proiezione Valore Futuro</div><div class="kpi-value">€ {valore_futuro:.2f}</div></div>',
            unsafe_allow_html=True)

    # Grafico lineare
    fig_line = px.line(
        df,
        x=df.index,
        y='Valore Investimento',
        title=f'Crescita del tuo investimento in {selected_symbol}')

    # Calcolo per il grafico a torta
    revenue = valore_attuale - investimento_iniziale
    labels = ['Investimento Iniziale', 'Rendimento']
    values = [investimento_iniziale, revenue]

    # Grafico a torta
    fig_pie = px.pie(values=values,
                     names=labels,
                     title='Breakdown Valore Attuale')

    # Mostra i grafici fianco a fianco
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_line)
    with col2:
        st.plotly_chart(fig_pie)




    #Mostra la checkbox per la tabella di storico dei dati
    on_dataTable = st.checkbox(
        "Mostra la tabella di storico per il periodo selezionato")


    if on_dataTable:
         # Mostra la tabella dei dati
        st.header("Dati Storici")
        st.write(df)



if __name__ == "__main__":
    run_streamlit_app()
