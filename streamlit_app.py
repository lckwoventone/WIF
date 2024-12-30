import streamlit as st
import yfinance as yf
import pandas as pd

# Funzione per calcolare i KPI
def calculate_kpis(historical_data, investment, start_year):
    historical_data['Date'] = pd.to_datetime(historical_data.index)
    filtered_data = historical_data[historical_data['Date'].dt.year >= start_year]

    if filtered_data.empty:
        return {
            "growth_rate": None,
            "current_value": None,
            "future_value": None,
            "error": f"Nessun dato disponibile dal {start_year}."
        }

    start_price = filtered_data.iloc[0]['Close']
    current_price = filtered_data.iloc[-1]['Close']

    years = (filtered_data.iloc[-1]['Date'] - filtered_data.iloc[0]['Date']).days / 365.25
    growth_rate = ((current_price / start_price) ** (1 / years) - 1) * 100 if years > 0 else None

    current_value = investment * (current_price / start_price)
    future_value = current_value * ((1 + growth_rate / 100) ** 5) if growth_rate is not None else None

    return {
        "growth_rate": round(growth_rate, 2) if growth_rate is not None else None,
        "current_value": round(current_value, 2) if current_value is not None else None,
        "future_value": round(future_value, 2) if future_value is not None else None,
    }

# Streamlit app
st.title("Analisi KPI di Indici Finanziari")

# Selezione dell'indice
st.sidebar.header("Seleziona un titolo")
symbols = {
    "Google": "GOOGL",
    "Apple": "AAPL",
    "Vanguard S&P 500 ETF": "VUSA",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
}
selected_symbol = st.sidebar.selectbox("Titolo", list(symbols.keys()))
symbol = symbols[selected_symbol]

# Input utente
investment = st.sidebar.number_input("Importo iniziale (€)", min_value=0.0, value=1000.0)
start_year = st.sidebar.number_input("Anno di partenza", min_value=1900, value=2010)

# Recupero dati da Yahoo Finance
try:
    with st.spinner("Caricamento dati..."):
        data = yf.download(symbol, start=f"{start_year}-01-01")
    st.success("Dati caricati con successo!")

    # Mostra grafico
    st.subheader(f"Andamento storico di {selected_symbol}")
    st.line_chart(data['Close'])

    # Calcolo KPI
    kpis = calculate_kpis(data, investment, start_year)

    # Mostra KPI
    if kpis.get("error"):
        st.error(kpis["error"])
    else:
        st.subheader("Risultati KPI")
        st.metric("Tasso di crescita medio annuo (CAGR)", f"{kpis['growth_rate']}%")
        st.metric("Valore attuale", f"€{kpis['current_value']}")
        st.metric("Valore futuro stimato (5 anni)", f"€{kpis['future_value']}")

except Exception as e:
    st.error(f"Errore durante il recupero dei dati: {str(e)}")
