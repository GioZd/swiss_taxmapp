import os
import warnings

from datetime import datetime

import polars as pl
import polars.selectors as cs

# from icecream import ic
from utils import COLNAMES_RATES, COLNAMES_SCALES, TAXABLE_ENTITIES


def _clean_rates(year: int = 2023) -> pl.DataFrame: # completed
    file_path = "data/rates/estv_rates_{}.xlsx"
    rates = pl.read_excel(
        file_path.format(year),
        has_header=False, 
        engine='xlsx2csv'
    )
    rates = rates.drop(cs.last())
    rates.columns = COLNAMES_RATES
    rates = rates.slice(4)
    return (
        rates.select(
            pl.col('canton_ID').cast(pl.Int64), 
            pl.col('canton'), 
            pl.col('FSO_ID').cast(pl.Int64), 
            pl.col('commune'),
            pl.all()
            .exclude('canton_ID', 'canton', 'FSO_ID', 'commune')
            .cast(pl.Float64) / 100          
        )
    )

def retrieve_multipliers(rates_df: pl.DataFrame, # completed
    commune: str) -> dict[str, float] | None:
    # commune = commune.lower()
    multipliers = (
        rates_df.filter(pl.col("commune")
                .str.contains(commune, literal=True))
    )
    # print(multipliers.to_dicts()[0])
    multipliers = (
        multipliers.select(
            pl.col('canton_ID').cast(pl.Int64), 
            pl.col('canton'), 
            pl.col('FSO_ID').cast(pl.Int64), 
            pl.col('commune'),
            pl.all()
            .exclude('canton_ID', 'canton', 'FSO_ID', 'commune')
            .cast(pl.Float64) / 100
        )
        .to_dicts()
    )
    return None if len(multipliers) == 0 else multipliers[0]


def retrieve_multipliers_by_year( # completed
    commune: str, 
    latest_year: int = datetime.today().year
) -> dict[str, float]:
    file_path = f"data/rates/estv_rates_{latest_year}.xlsx"
    multipliers = None
    while os.path.exists(file_path) and multipliers is None:
        rates = pl.read_excel(
            f"data/rates/estv_rates_{latest_year}.xlsx",
            has_header=False, 
            engine='xlsx2csv'
        )
        rates = rates.drop(cs.last()) # last is null column
        rates.columns = COLNAMES_RATES
        multipliers = retrieve_multipliers(rates, commune)
        latest_year -= 1
    return multipliers     


def _clean_scales(canton: str, type_of_tax: str = 'income',
                  latest_year: int = datetime.today().year) -> pl.DataFrame: # incomplete
    if type_of_tax.lower() not in ['income', 'assets']:
        raise ValueError('`type_of_tax` should be either "income" or "assets"')
    
    file_path = "data/scales/{}/{}/estv_scales_{}.xlsx"
    while (not os.path.isfile(file_path.format(type_of_tax, latest_year, canton))
           and latest_year >= 2010):
        latest_year -= 1
    if not os.path.isfile(file_path.format(type_of_tax, latest_year, canton)):
        warnings.warn(
            f"File {file_path.format(type_of_tax, latest_year, canton)}"
            f" could not be retrieved. Check validity of canton or year."
        )
        return pl.DataFrame(dict.fromkeys(COLNAMES_SCALES))
    
    scales = pl.read_excel(
        file_path.format(type_of_tax, latest_year, canton),
        has_header=False, 
        engine='xlsx2csv'            
    )

    # last 3 columns are null, first three rows are irrelevant
    scales = scales.drop(cs.last()).drop(cs.last()).drop(cs.last())
    scales = scales.slice(4)
    scales.columns = COLNAMES_SCALES

    return (
        scales.select(
            pl.col('canton_ID').cast(pl.Int64),
            *COLNAMES_SCALES[1:5],
            pl.col('taxable_worth').cast(pl.Float64),
            pl.col('additional_percentage').cast(pl.Float64)/100,
            pl.col('base_amount_CHF').cast(pl.Float64)
        )
    )


def _select_scales(
    canton: str,
    taxable_entity: str = 'single',
    **kwargs
) -> pl.DataFrame:
    if taxable_entity not in ['single', 'with_family', 'all']:
        raise ValueError(
            f"'{taxable_entity}' is not a valid taxable entity."
            f" Try one of the following: 'single', 'with_family' or 'all'"
        )
    if kwargs.get('type_of_tax') in ['income', None] and taxable_entity == 'all':
        raise ValueError('income tax does not have a taxable entity "all"')
    if kwargs.get('type_of_tax') == 'assets' and taxable_entity != 'all':
        raise ValueError('assets tax has one single allowed' 
                         ' taxable entity named "all"')
    return(
        _clean_scales(canton, **kwargs).filter(
            pl.col('taxable_entity').str.strip_chars()
            .is_in(TAXABLE_ENTITIES[taxable_entity])
        )
    )

def _calculate_tax_base(net_worth: float, canton: str, **kwargs) -> float:
    scales = _select_scales(
        canton, 
        taxable_entity = kwargs.get('taxable_entity', 'single'), 
        type_of_tax = kwargs.get('type_of_tax', 'income'),
        latest_year = kwargs.get('latest_year', 2023)
    )
    row = scales.filter(pl.col('taxable_worth') <= net_worth).to_dicts()[-1]
    base = row['base_amount_CHF']
    increment = row['additional_percentage'] * (net_worth - base)
    return base + increment
   

def show_taxes(net_worth: float) -> None:
    table = _clean_rates()
    print(
        table.with_columns(
            cantonal_tax = (
                pl.col('income_canton')
                .mul(_calculate_tax_base(net_worth, 'TI'))
            ),
            communal_tax = (
                pl.col('income_commune')
                * _calculate_tax_base(net_worth, 'TI')
            )
        )
        
    )

def _read_table():
    table = pl.read_excel(
        "data/rates/estv_rates_2023.xlsx",
        has_header=False, engine='xlsx2csv'
    )
    table = table.drop(cs.last())
    table.columns = COLNAMES_RATES
    table = table.slice(4)
    print(table)

if __name__ == '__main__':
    _read_table()
    # print(retrieve_multipliers(table, 'Adliswil'))
    # print(retrieve_multipliers_by_year('Lugano'))
    # print(_clean_scales('TI', 'income', 2024))
    # print(_clean_scales('TI', 'assets', 2024))
    # print(_select_scales('TI', 'with_family', latest_year=2023))
    # print(_clean_rates(2023))
    # print(_calculate_tax_base(80000, 'TI'))
    # show_taxes(80000)