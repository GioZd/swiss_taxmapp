import os
from datetime import datetime
from functools import partial
from math import sqrt
from time import sleep, time

import altair as alt
import geopandas as gpd
import polars as pl
import streamlit as st
from streamlit.components.v1 import html

from utils import (
    download_all, fill_all_taxes, 
    _try_download, TAX_GROUPS
)


@st.cache_data
def get_table(income: float, assets: float, **kwargs) -> pl.DataFrame:
    return fill_all_taxes(income, assets, **kwargs)


def display_table(income: float, assets: float, **kwargs) -> None:
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
    table = get_table(income, assets, **kwargs).select(column_names.keys())
    options = ['All cantons']
    options.extend(table['canton'].unique().sort())
    canton = st.pills('Filter by canton', options, default='All cantons')
    if canton == 'All cantons':
        table = table.sort(by='total')
        st.dataframe(table, column_config=column_names)
    else:
        table = (
            table
            .sort(by='total')
            .filter(pl.col('canton').is_in([canton]))
        )
        st.dataframe(table, column_config = column_names) 
    # st.download_button(
    #     label = "Download data as CSV file",
    #     data  = table.write_csv(),
    #     file_name = f'taxes_{'_'.join(canton.split()).upper()}.csv',
    #     mime = "text/csv",
    # ) # streamlit can make it by default, so it's redundant

@st.cache_data
def create_map(income: float, assets: float, 
               canton: str = 'All cantons', **kwargs) -> alt.Chart:
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
    table = get_table(income, assets, **kwargs)
    layer1 = (
        alt.Chart(sdf)
        .mark_geoshape(stroke='white', strokeWidth=3, color='null')
        .properties(width=600)        
    )
    layer2 = (
        alt.Chart(kdf)
        .mark_geoshape(stroke='white', strokeWidth=1, color='null')
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
                scheme = 'redyellowblue', # 'redyellowgreen' not colorblind-friendly
                # type = 'quantize',
                reverse = True
            )
        )
        .properties(width=600)          
    )
    annotation = (
        alt.Chart(pl.DataFrame({'text': ['Kartengrundlage: © BFS']}))
        .transform_calculate(
            x = '600',
            y = '0'
        )
        .mark_text(
            align='right',
            baseline='bottom',
            fontSize=12,
            color='lightgrey'
        ).encode(
            alt.Text('text:N'),
            alt.X('x:Q').scale(domain=[0, 600]),
            alt.Y('y:Q').scale(domain=[0,400])
        )
    )
    swissmap: alt.LayerChart = (layer3 + top_layer + layer2 + layer1)
    if canton != 'All cantons':
        swissmap = swissmap.project(        
            # clipExtent = [[bounds.minx, bounds.miny], [bounds.maxx, bounds.maxy]]
            center = (center.x, center.y),
            scale = 10_000 / sqrt(deltamax)
        )

    return (
        alt.layer(swissmap, annotation)
        .resolve_axis(x='independent', y='independent')
        .configure(background='null')
        .configure_axis(disable=True)
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
        .configure_view(strokeWidth=0)
    )


def add_map(chart: alt.Chart) -> None:
    """Salva la mappa come file html e la carica in streamlit"""
    if not os.path.isdir('cachedata'):
        os.mkdir('cachedata')
    chart.save('cachedata/map.html', embed_options={'renderer':'svg'})
    with open('cachedata/map.html') as fp:
        html(fp.read(), height=500)


def show_map(income: float, assets: float, **kwargs) -> None:
    table = get_table(income, assets, **kwargs)
    options = ['All cantons']
    options.extend(table['canton'].unique().sort())
    canton = st.pills(
        'Filter by canton', options, 
        default='All cantons', key="pills1"
    )
    add_map(create_map(income, assets, canton, **kwargs))


def show_1v1(**kwargs):
    income, assets = get_user_inputs('k1', 'k2')
    table = get_table(income, assets, **kwargs)
    st.divider()
    sx, central, dx = st.columns([4,1,4], vertical_alignment='bottom')
    options = ['All cantons']
    options.extend(table['canton'].unique().sort())
    # swap = central.button(':material/sync_alt:')
    default1, default2 = table['commune'].unique().sort()[:2]
    with sx:
        canton_sx = st.pills(
            'Filter by canton', options, 
            default='All cantons', key="pills_sx"
        )
        if canton_sx == 'All cantons':
            sel1 = table.filter(pl.col('commune') != default2)
        else:
            sel1 = table.filter(
                (pl.col('canton').is_in([canton_sx]))
                & (pl.col('commune') != st.session_state.get('city2', default2))
            )
        city1 = st.selectbox(
            'Select commune', 
            sel1['commune'].unique().sort(), 
            key='city1'
        )

    with dx:
        canton_dx = st.pills(
            'Filter by canton', options, 
            default='All cantons', key="pills_dx"
        )
        if canton_dx == 'All cantons':
            sel2 = table.filter(
                pl.col('commune') != st.session_state.get('city1', default1)
            )
        else:
            sel2 = table.filter(
                (pl.col('canton').is_in([canton_dx]))
                & (pl.col('commune') != city1)
            )
        city2 = st.selectbox(
            'Select commune', 
            sel2['commune'].unique().sort(), 
            key='city2'
        )
    
    row1 = table.filter(pl.col('commune') == city1)
    row2 = table.filter(pl.col('commune') == city2)
    cmp_data = (
        pl.concat([row1, row2])
        .unpivot(index = ['canton_ID', 'canton', 'FSO_ID', 'commune'])
        .with_columns(
            pl.when(pl.col('commune')==city1)
            .then(-1)
            .otherwise(1)
            .alias('factor'),
            pl.col('variable')
            .str.replace_all('_', ' ')
            .str.to_titlecase()
        )
        .with_columns(
            pl.when(pl.col('variable').str.contains('Income'))
            .then(pl.lit('Income Tax')).otherwise(
            pl.when(pl.col('variable').str.contains('Assets'))
            .then(pl.lit('Assets Tax')).otherwise(
            pl.when(pl.col('variable').str.contains('Federal'))
            .then(pl.lit('Federal Tax')).otherwise(pl.lit('Total'))    
            ))
            .alias('category')
        )
    )
    # st.write(cmp_data)
    custom_order = [
        'cantonal_income_tax', 'communal_income_tax',
        'income_tax', 'cantonal_assets_tax',
        'communal_assets_tax', 'assets_tax',
        'federal_tax', 'total'
    ]
    custom_order = [v.replace('_', ' ').title() for v in custom_order]
    basechart = (
        alt.Chart(cmp_data)
        .transform_calculate(x = 'datum.value * datum.factor')
        .mark_bar(color='#EEEEEE', stroke='lightslategrey', strokeWidth=1.5)
        .encode(
            alt.X('x:Q'),
            alt.Y('variable', sort=custom_order),
            # alt.Color('value', title='CHF').scale(
            #     scheme = 'redyellowblue',
            #     reverse = True,
            #     domain = [table['total'].min(), table['total'].max()]
            #     # type = 'quantize'
            # )
        )
    )
    total_table = cmp_data.filter(
        pl.col('variable').is_in(['Income Tax', 'Assets Tax', 'Total'])
    )
    total_chart = (
        alt.Chart(total_table)
        .transform_calculate(
            x = 'datum.value * datum.factor',
            opacity = 'datum.variable=="Total" ? 1 : 1'
        )
        .mark_bar(strokeWidth=1.5, stroke='#EEEEEE')
        .encode(
            alt.X('x:Q', title='Taxation CHF'),
            alt.Y('variable', sort=custom_order),
            alt.Color('value', title='CHF').scale(
                scheme = 'redyellowblue',
                reverse = True,
                domain = [table['total'].min(), table['total'].max()]
                # type = 'quantize'
            ),
            # alt.Opacity('opacity:Q', legend=None)
        )
    )
    chart = (
        (basechart + total_chart)
        .resolve_axis(y='shared')
        .resolve_scale(color='shared')
        .resolve_legend(color='independent')
        .encode(alt.Tooltip(['commune:N', 'variable:N', 'value:Q']))
        # .properties(background=None)
        # .facet('category')
        .configure_axisX(labelExpr='abs(datum.value)', title=None, domain=True)
        .configure_axisY(title=None, labelLimit=240, domainWidth=3)
        .configure_legend(
            titleOrient='top', 
            titleAlign='left', 
            gradientStrokeWidth=1.5, 
            gradientStrokeColor='lightgrey'
        )
    )
    baseline = (
        alt.Chart(pl.DataFrame({'x': [0]}))
        .mark_rule(stroke='red', strokeWidth=4)
        .encode(alt.X('x:Q'))
    )
    # st.altair_chart(basechart, use_container_width=True)
    st.altair_chart(chart+baseline, use_container_width=True)
    column_names = {
        'canton_ID': 'Canton ID',
        'canton': 'Canton',
        'FSO_ID': st.column_config.NumberColumn("FSO ID", format="%d"),
        'commune': 'Commune',
        'federal_tax': st.column_config.NumberColumn("Federal Tax", format="%.2f"),
        'cantonal_income_tax': st.column_config.NumberColumn("(Canton) Income Tax", format="%.2f"),
        'communal_income_tax': st.column_config.NumberColumn("(Commune) Income Tax", format="%.2f"),
        'income_tax': st.column_config.NumberColumn("Income Tax", format="%.2f"),
        'cantonal_assets_tax': st.column_config.NumberColumn("(Canton) Assets Tax", format="%.2f"),
        'communal_assets_tax': st.column_config.NumberColumn("(Commune) Assets Tax", format="%.2f"),
        'assets_tax': st.column_config.NumberColumn("Assets Tax", format="%.2f"),
        'total': st.column_config.NumberColumn("Total", format="%.2f"),
    }
    st.dataframe(pl.concat([row1, row2]), use_container_width=True, column_config=column_names)


def download_data(year: int = datetime.today().year):
    t0 = time()
    text = 'Download {}/54. {:.0f}m{:.0f}s to end.'
    my_bar = st.progress(1, text=text.format(0, 5, 0))
    for adv, key in enumerate(TAX_GROUPS.keys(), 1):
        try:
            _try_download(key, year, taxType='income', rs='scales')
            t1 = time()
            left_time = (54-adv)*(t1-t0)/adv
            mins, secs = divmod(left_time, 60)
            my_bar.progress(round(adv*1.5), text=text.format(adv, mins, secs))
        except Exception as e:
            pass
    for adv, key in enumerate(TAX_GROUPS.keys(), 27):
        try:
            _try_download(key, year, taxType='assets', rs='scales')
            t1 = time()
            left_time = (54-adv)*(t1-t0)/adv
            mins, secs = divmod(left_time, 60)
            my_bar.progress(round(adv*1.5), text=text.format(adv, mins, secs))
        except Exception as e:
            pass
    try:
        _try_download(99, year)
        my_bar.progress(100)
    except Exception as e:
        pass
    sleep(3)
    my_bar.empty()


def get_last_update() -> datetime:
    with open('data/.timestamp.txt') as file:
        last_update = file.read().strip()
    if last_update:
        return datetime.fromisoformat(last_update.splitlines()[0])
    else:
        return datetime.min


def config_download(year: int = datetime.today().year) -> None:
    lc, _, rc= st.columns([1,2,1])
    now = datetime.now()
    last = get_last_update()
    if (now - last).days >= 0: # set to 7 to show once a week
        button_placeholder = rc.empty()
        download_button = button_placeholder.button(
            'Get newer data', icon=':material/cloud:',  key='download_button'
        )
        try:
            if download_button:
                button_placeholder.empty()
                with rc:
                    with st.spinner("Downloading..."):
                        download_data(year)
                with open('data/.timestamp.txt', 'w') as timestamp:
                    now = datetime.now()
                    timestamp.write(now.isoformat(sep=' ', timespec='seconds'))
                button_placeholder.success('Data downloaded successfully!')
        except Exception as e:
            button_placeholder.error(f'{e}. Please, retry later.')
            sleep(10)
            download_button = button_placeholder.button(
                'Get newer data', 
                icon=':material/cloud:',  
                key='download_button'
            )


def get_user_inputs(key1: str | None = None, 
                    key2: str | None = None) -> tuple[float, float]:
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input(
            'Taxable income', min_value=0, 
            step=5000, value=50_000,
            key = key1
        )
        st.write(f"CHF {income:,.2f}")
    with col2:
        assets = st.number_input(
            'Taxable assets', min_value=0, 
            step=20000, value=500_000,
            key = key2
        )
        st.write(f"CHF {assets:,.2f}")
    return float(income), float(assets)


def get_readme() -> str:
    with open('README.md', 'r') as file:
        readme = file.readlines()
    return '\n'.join(readme[1:])


def page_config() -> None:
    st.set_page_config(
        page_title = 'Taxmapp: The Ultimate Swiss Taxes Internal Comparator', 
        page_icon = ':helmet_with_white_cross:',
        # menu_items = {'About': get_readme()}
    )


def navigation() -> None:
    nav, _ = st.columns([1,2])
    p1, p2, p3 = nav.columns(3)
    p1.page_link(st.Page(homepage, title='Home :material/house:'))
    p2.page_link(st.Page(one_to_one, title='1v1 :material/compare_arrows:'))
    p3.page_link(st.Page(about, title='About :material/info:'))


def select_year() -> int:
    with st.sidebar:
        st.html(
            """<p style="text-align: justify; font-size: 80%; margin: 0">
            If you can't find your desired city or too many spots on the 
            map seem to be missing, please try referring to one of the 
            previous years by using the widget below.</p>
            """
        )
        oldest = 2022
        newest = datetime.today().year
        # year = st.select_slider(
        #     'Select year', 
        #     options=list(range(oldest, newest+1))
        # )
        year = st.number_input(
            'Select year', 
            min_value=oldest, 
            max_value=newest, 
            value=newest
        )
        st.divider()
    return year


def choose_language() -> str:
    language = st.sidebar.selectbox('Select language', ['EN'])
    return language


def homepage(**kwargs):
    income, assets = get_user_inputs()
    tab1, tab2 = st.tabs(['Map :material/map:', 'Table :material/table:'])
    with tab1:
        show_map(income, assets, **kwargs)
    with tab2:
        display_table(income, assets, **kwargs)
    config_download()


def one_to_one(**kwargs) -> None:
    show_1v1(**kwargs)
    config_download()


def about():
    st.write(get_readme())


def main():
    page_config()
    # navigation()
    year = select_year()
    language = choose_language()
    st.image('elements/taxmapp.svg', use_container_width=True)
    pg = st.navigation([
        st.Page(
            partial(homepage, latest_year=year).func, 
            default=True, title='Home',
            icon=':material/house:'
        ), 
        st.Page(
            partial(one_to_one, latest_year=year).func, 
            title='1v1', icon=':material/compare_arrows:'
        ),
        st.Page(about, icon=':material/info:', title='About')
    ])
    pg.run()


if __name__ == '__main__':
    main()