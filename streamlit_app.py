import streamlit as st
import pandas as pd

# Funzione KPI integrata
def calculate_kpis(historical_data, investment, start_year):
    """
    Calcola i KPI per un investimento.

    Args:
        historical_data (pd.DataFrame): Dati storici con colonne ['Date', 'Close'].
        investment (float): Importo iniziale dell'investimento.
        start_year (int): Anno di partenza per l'investimento.

    Returns:
        dict: KPI calcolati, inclusi tasso di crescita medio annuo, valore attuale e futuro.
    """
    # Filtra i dati per l'anno di inizio
    historical_data['Date'] = pd.to_datetime(historical_data['Date'])
    filtered_data = historical_data[historical_data['Date'].dt.year >= start_year]

    if filtered_data.empty:
        return {
            "growth_rate": None,
            "current_value": None,
            "future_value": None,
            "error": f"Nessun dato disponibile dal {start_year}."
        }

    # Calcola il prezzo iniziale e attuale
    start_price = filtered_data.iloc[0]['Close']
    current_price = filtered_data.iloc[-1]['Close']

    # Tasso di crescita medio annuo (CAGR)
    years = (filtered_data.iloc[-1]['Date'] - filtered_data.iloc[0]['Date']).days / 365.25
    growth_rate = ((current_price / start_price) ** (1 / years) - 1) * 100 if years > 0 else None

    # Valore attuale
    current_value = investment * (current_price / start_price)

    # Valore futuro stimato (5 anni con CAGR)
    future_value = current_value * ((1 + growth_rate / 100) ** 5) if growth_rate is not None else None

    # Aggiungi un controllo per evitare di arrotondare valori None
    return {
        "growth_rate": round(growth_rate, 2) if growth_rate is not None else None,
        "current_value": round(current_value, 2) if current_value is not None else None,
        "future_value": round(future_value, 2) if future_value is not None else None,
    }

# Streamlit App
st.title("Calcolo KPI per Investimenti")

# Input da utente
uploaded_file = st.file_uploader("Carica un file CSV con dati storici (Date, Close)", type=["csv"])
investment = st.number_input("Inserisci l'importo dell'investimento iniziale", min_value=0.0, value=1000.0)
start_year = st.number_input("Inserisci l'anno di partenza per l'investimento", min_value=1900, value=2000)

if uploaded_file is not None:
    try:
        # Legge il file CSV
        historical_data = pd.read_csv(uploaded_file)
        st.write("Dati caricati con successo:")
        st.dataframe(historical_data)

        # Calcolo KPI
        kpis = calculate_kpis(historical_data, investment, start_year)

        # Mostra i risultati
        if kpis.get("error"):
            st.error(kpis["error"])
        else:
            st.subheader("Risultati KPI")
            st.metric("Tasso di crescita medio annuo (CAGR)", f"{kpis['growth_rate']}%")
            st.metric("Valore attuale", f"${kpis['current_value']}")
            st.metric("Valore futuro stimato (5 anni)", f"${kpis['future_value']}")

    except Exception as e:
        st.error(f"Errore nell'elaborazione dei dati: {str(e)}")
