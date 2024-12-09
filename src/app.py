import locale

import altair as alt
import polars as pl
import streamlit as st

from utils import fill_all_taxes, fill_taxes

@st.cache_data
def get_table(income: float, assets: float) -> pl.DataFrame:
    return fill_all_taxes(income, assets)

def display_table(income: float, assets: float) -> None:
    column_names = {
        'canton_ID': 'Canton ID',
        'canton': 'Canton',
        'FSO_ID': 'FSO ID',
        'commune': 'Commune',
        'federal_tax': st.column_config.NumberColumn("Federal Tax", format="%.2f"),
        'income_tax': st.column_config.NumberColumn("Income Tax", format="%.2f"),
        'assets_tax': st.column_config.NumberColumn("Assets Tax", format="%.2f"),
        'total': st.column_config.NumberColumn("Total", format="%.2f"),
    }
    table = get_table(income, assets)
    options = ['All cantons']
    options.extend(table['canton'].unique().sort())
    canton = st.pills('Filter by canton', options, default='All cantons')
    if canton == 'All cantons':
        st.dataframe(table.sort(by='total'), column_config=column_names)
    else:
        st.dataframe(
            table
            .sort(by='total')
            .filter(pl.col('canton').is_in([canton])),
            column_config = column_names
        )   

@st.cache_data
def create_map() -> alt.Chart:
    pass

def show_map(income: float, assets: float):
    table = get_table(income, assets)
    options = ['All cantons']
    options.extend(table['canton'].unique().sort())
    canton = st.pills('Filter by canton', options, default='All cantons', key="pills1")


def get_user_inputs() -> tuple[float, float]:
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input(
            'Taxable income', min_value=0, 
            step=5000, value=50_000
        )
        st.write(f"CHF {income:,.2f}")
    with col2:
        assets = st.number_input(
            'Taxable assets', min_value=0, 
            step=20000, value=500_000
        )
        st.write(f"CHF {assets:,.2f}")
    return float(income), float(assets)

def main():
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    st.image('elements/taxmapp.png', use_container_width=True)
    income, assets = get_user_inputs()
    tab1, tab2 = st.tabs(['Map 🗺️', 'Table 🔢'])
    with tab1:
        show_map(income, assets)
        st.write('Devo implementare la mappa!!!')
    with tab2:
        display_table(income, assets)


if __name__ == '__main__':
    main()