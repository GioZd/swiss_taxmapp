import locale
import os
from math import sqrt

import altair as alt
import geopandas as gpd
import polars as pl
import streamlit as st
from streamlit.components.v1 import html

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
def create_map(income: float, assets: float, canton: str = 'All cantons') -> alt.Chart:
    PATH_S = (
        './geodata/2024_GEOM_TK/01_INST'
        '/Gesamtfläche_gf/K4_suis18480101_gf'
        '/K4suis18480101gf_ch2007Poly.shp'
    )
    PATH_K = (
        './geodata/2024_GEOM_TK/01_INST'
        '/Gesamtfläche_gf/K4_kant20220101_gf'
        '/K4kant20220101gf_ch2007Poly.shp'
    )
    PATH_G = (
        './geodata/2024_GEOM_TK/01_INST'
        '/Gesamtfläche_gf/K4_polg20240101_gf'
        '/K4polg20240101gf_ch2007Poly.shp'
    )
    sdf: gpd.GeoDataFrame = gpd.read_file(PATH_S).to_crs("EPSG:4326")
    kdf: gpd.GeoDataFrame = gpd.read_file(PATH_K).to_crs("EPSG:4326")
    gdf: gpd.GeoDataFrame = gpd.read_file(PATH_G).to_crs("EPSG:4326")
    gdf['id_i64'] = gdf['id'].astype(int)
    table = get_table(income, assets)
    layer1 = (
        alt.Chart(sdf)
        .mark_geoshape(stroke='white', strokeWidth=3, color='null')
        .properties(width=600)        
    )
    layer2 = (
        alt.Chart(kdf)
        .mark_geoshape(stroke='white', strokeWidth=1.5, color='null')
        .properties(width=600) 
      
    )
    layer3 = (
        alt.Chart(gdf)
        .mark_geoshape(stroke='white', strokeWidth=0.2, color='lightslategray')
        .properties(width=600)       
    )
    domain = [table['total'].min(), table['total'].max()]
    if canton == 'All cantons':
        sel = table.to_pandas()
        center = sdf.centroid[0]
        bounds = sdf.bounds.iloc[0]
    else:
        sel = table.filter(pl.col('canton').is_in([canton])).to_pandas()
        canton_id = sel['canton_ID'].iloc[0]
        center = kdf.centroid[canton_id-1]
        bounds = kdf.bounds.iloc[canton_id-1]
    deltamax = max(bounds.maxx-bounds.minx, bounds.maxy-bounds.miny)
    gdf_data = gdf.merge(sel, left_on='id_i64', right_on='FSO_ID')
    gdf_data['Overall taxes CHF'] = gdf_data['total']  
    top_layer = (
        alt.Chart(gdf_data)
        .mark_geoshape(stroke='white', strokeWidth=0.2)
        .encode(
            alt.Color('Overall taxes CHF').scale(
                domain = domain,
                scheme = 'redyellowgreen',
                # type = 'quantize',
                reverse = True
            )
        )
        .properties(width=600)          
    )
    swissmap: alt.LayerChart = (layer3 + layer2 + layer1 + top_layer)
    if canton != 'All cantons':
        swissmap = swissmap.project(        
            # clipExtent = [[bounds.minx, bounds.miny], [bounds.maxx, bounds.maxy]]
            center = (center.x, center.y),
            scale = 10_000 / sqrt(deltamax)
        )

    return (
        swissmap
        .configure(background='null')
        .configure_legend(
            strokeColor='grey',
            fillColor='#EEEEEE',
            padding=10,
            cornerRadius=10,
            orient='top',
            titleFontWeight='bold',
            titleColor='black',
            labelColor='black'
        )
    )


def add_map(chart: alt.Chart) -> None:
    """Salva la mappa come file html e la carica in streamlit"""
    if not os.path.isdir('cachedata'):
        os.mkdir('cachedata')
    chart.save('cachedata/map.html', embed_options={'renderer':'svg'})
    with open('cachedata/map.html') as fp:
        html(fp.read(), height=500)


def show_map(income: float, assets: float):
    table = get_table(income, assets)
    options = ['All cantons']
    options.extend(table['canton'].unique().sort())
    canton = st.pills('Filter by canton', options, default='All cantons', key="pills1")
    add_map(create_map(income, assets, canton))


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
    with tab2:
        display_table(income, assets)


if __name__ == '__main__':
    main()