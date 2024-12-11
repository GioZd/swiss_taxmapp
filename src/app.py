import json
import locale

import altair as alt
import geopandas as gpd
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
        'FSO_ID': st.column_config.NumberColumn("FSO ID", format="%d"),
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
def create_map(income, assets) -> alt.Chart:
    gdf: gpd.GeoDataFrame = gpd.read_file('./data/geodata/2024_GEOM_TK/01_INST/Gesamtfläche_gf/K4_kant20220101_gf/K4kant20220101gf_ch2007Poly.shp').to_crs("EPSG:4326")
    gdf_json = gdf.to_json()
    geojson = json.loads(gdf_json)
    st.write(gdf)
    st.json(geojson, expanded=False)
    # st.write(type(gdf))
    # gdf.plot.area()
    # st.write(geojson['features'], expanded=False)
    source = get_table(income, assets)
    with open('data/output.json', 'w') as output: 
        output.write(json.dumps(geojson))
    regions = alt.topo_feature('data/output.json', 'properties')
    return alt.Chart(regions).mark_geoshape().encode(
            alt.Color('total:Q').scale(scheme='viridis')
    ).transform_lookup(
        lookup='total',
        from_=alt.LookupData(source, 'id', ['total'])
    )

def show_map(income: float, assets: float):
    table = get_table(income, assets)
    options = ['All cantons']
    options.extend(table['canton'].unique().sort())
    canton = st.pills('Filter by canton', options, default='All cantons', key="pills1")
    st.altair_chart(create_map(income, assets))


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