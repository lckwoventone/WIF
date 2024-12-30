import pandas as pd
import pandas_datareader.data as web
from datetime import datetime
import streamlit as st

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

    return {
        "growth_rate": round(growth_rate, 2),
        "current_value": round(current_value, 2),
        "future_value": round(future_value, 2),
    }

def main():
    st.title("Analisi KPI di Investimenti")

    # Input utente
    ticker = st.text_input("Inserisci il simbolo del titolo (es. AAPL, GOOGL):", "AAPL")
    start_year = st.number_input("Anno di inizio dell'investimento:", min_value=1900, max_value=datetime.now().year, value=2020)
    investment = st.number_input("Importo iniziale dell'investimento:", min_value=0.0, value=1000.0, step=100.0)

    if st.button("Calcola KPI"):
        try:
            # Ottieni i dati finanziari
            start_date = f"{start_year}-01-01"
            end_date = datetime.now().strftime("%Y-%m-%d")

            data = web.DataReader(ticker, 'yahoo', start_date, end_date)
            data.reset_index(inplace=True)
            data = data[['Date', 'Close']]

            # Calcola i KPI
            kpis = calculate_kpis(data, investment, start_year)

            # Mostra i risultati
            if kpis.get("error"):
                st.error(kpis["error"])
            else:
                st.metric("Tasso di crescita annuo (CAGR)", f"{kpis['growth_rate']}%")
                st.metric("Valore attuale", f"${kpis['current_value']}")
                st.metric("Valore futuro stimato (5 anni)", f"${kpis['future_value']}")

                # Mostra il grafico
                st.line_chart(data.set_index('Date')['Close'])
        except Exception as e:
            st.error(f"Errore durante il calcolo: {str(e)}")

if __name__ == "__main__":
    main()
