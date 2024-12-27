import streamlit as st
from app.kpi_calculator import calculate_kpis
from app.plotter import plot_graph
from app.data_loader import load_historical_data

st.title("What IF - What is Finance")
st.sidebar.header("Benvenuto!")

# Sezione per selezionare un simbolo
symbol = st.sidebar.text_input("Inserisci il simbolo di un'azione o ETF:", "AAPL")

# Input utente
investment = st.sidebar.number_input("Inserisci il tuo investimento (€):", value=2000)
start_year = st.sidebar.number_input("Anno di partenza:", value=2010)

# Calcolo KPI
if st.sidebar.button("Calcola KPI"):
    kpis = calculate_kpis(symbol, investment, start_year)
    st.metric("Tasso di crescita medio annuo", f"{kpis['growth_rate']:.2f}%")
    st.metric("Valore attuale", f"€{kpis['current_value']:.2f}")
    st.metric("Valore futuro stimato", f"€{kpis['future_value']:.2f}")

# Grafico
data = load_historical_data(symbol)
st.line_chart(data['Close'])

# Tabella dati storici
st.dataframe(data)


