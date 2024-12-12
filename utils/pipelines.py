import os
import sys
import warnings

from datetime import datetime
from functools import lru_cache
from math import log
from typing import Callable, Literal, TypeAlias

import polars as pl
import polars.selectors as cs

sys.path.append(os.path.dirname(sys.path[0]))

from utils import (
    COLNAMES_RATES, COLNAMES_SCALES_BASE, 
    COLNAMES_SCALES_DIFF, COLNAMES_SCALES_FLAT,
    COLNAMES_SCALES_FORMULA, TAX_AUTHORITIES,
    TAXABLE_ENTITIES,TAX_GROUPS
)

Authority: TypeAlias = Literal['canton', 'commune', 'federal']
TaxType: TypeAlias = Literal['income', 'assets']
MaritalStatus: TypeAlias = Literal['all', 'single', 'with_family']


def clean_rates(year: int = 2023) -> pl.DataFrame: # completed
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


def _read_scales_from_excel( # working
        canton: str, type_of_tax: TaxType = 'income',
        latest_year: int = datetime.today().year 
) -> pl.DataFrame | None: 
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
        return None
    
    scales = pl.read_excel(
        file_path.format(type_of_tax, latest_year, canton),
        has_header=False, 
        engine='xlsx2csv'            
    )
    return scales


def _crop_table(table: pl.DataFrame, offset: int = 4) -> pl.DataFrame: # working
    """Get rid of null rows and columns"""
    table = table.slice(offset)
    not_null_cols = filter(lambda x: x.null_count() != table.height, table)
    not_null_col_names = map(lambda x: x.name, not_null_cols)
    table = table.select(not_null_col_names)
    return table


def _clean_scales_base( # completed
        canton: str, type_of_tax: TaxType = 'income',
        latest_year: int = datetime.today().year
) -> pl.DataFrame: 
    scales = _read_scales_from_excel(canton, type_of_tax, latest_year)
    scales = _crop_table(scales)
    scales.columns = COLNAMES_SCALES_BASE
    return (
        scales.select(
            pl.col('canton_ID').str.replace(r'\-', '0').cast(pl.Int64),
            *COLNAMES_SCALES_BASE[1:5],
            pl.col('taxable_worth').cast(pl.Float64),
            pl.col('additional_percentage').cast(pl.Float64)/100,
            pl.col('base_amount_CHF').cast(pl.Float64)
        )
    )


def _clean_scales_diff( # working
        canton: str, type_of_tax: TaxType = 'income',
        latest_year: int = datetime.today().year
) -> pl.DataFrame: 
    scales = _read_scales_from_excel(canton, type_of_tax, latest_year)
    scales = _crop_table(scales)
    scales.columns = COLNAMES_SCALES_DIFF

    return (
        scales.select(
            pl.col('canton_ID').cast(pl.Int64),
            *COLNAMES_SCALES_DIFF[1:5],
            pl.col('to_next_CHF').cast(pl.Float64),
            pl.col('additional_percentage').cast(pl.Float64)/100
        )
    )


def _clean_scales_flat( # working
        canton: str, type_of_tax: TaxType = 'income',
        latest_year: int = datetime.today().year
) -> pl.DataFrame: 
    scales = _read_scales_from_excel(canton, type_of_tax, latest_year)
    scales = _crop_table(scales)
    scales.columns = COLNAMES_SCALES_FLAT

    return (
        scales.select(
            pl.col('canton_ID').cast(pl.Int64),
            *COLNAMES_SCALES_FLAT[1:5],
            pl.col('tax_rate').cast(pl.Float64)/100
        )
    )


def _clean_scales_formula( # working
        canton: str, type_of_tax: TaxType = 'income',
        latest_year: int = datetime.today().year
) -> pl.DataFrame: 
    scales = _read_scales_from_excel(canton, type_of_tax, latest_year)
    scales = _crop_table(scales)
    scales.columns = COLNAMES_SCALES_FORMULA

    return (
        scales.select(
            pl.col('canton_ID').cast(pl.Int64),
            *COLNAMES_SCALES_FLAT[1:5],
            pl.col('taxable_worth').cast(pl.Float64),
            pl.col("formula")
        )
    )

@lru_cache
def clean_scales( # working       
        canton: str, type_of_tax: str = 'income',
        latest_year: int = datetime.today().year
) -> pl.DataFrame: 
    kwargs = {
        "canton": canton,
        "type_of_tax": type_of_tax,
        "latest_year": latest_year
    }
    CLEANING_FUNCTIONS = [
        _clean_scales_base, _clean_scales_diff,
        _clean_scales_flat, _clean_scales_formula,

    ]
    # scales = _read_scales_from_excel(canton, type_of_tax, latest_year)
    # scales = _crop_table(scales, offset=0)
    # option = scales.row(3)[-1]
    # if option == 'Base amount CHF':
    #     return _clean_scales_base(**kwargs)
    for i in range(4):
        try: 
            return CLEANING_FUNCTIONS[i](**kwargs)
        except: 
            continue

@lru_cache
def select_scales( # in progress
    canton: str,
    taxable_entity: MaritalStatus = 'single',
    type_of_tax: TaxType = 'income',
    authority: Authority = 'canton',
    latest_year: int = datetime.today().year
) -> pl.DataFrame:
    if taxable_entity not in ['single', 'with_family', 'all']:
        raise ValueError(
            f"'{taxable_entity}' is not a valid taxable entity."
            f" Try one of the following: 'single', 'with_family' or 'all'"
        )
    if authority not in ['canton', 'commune', 'federal']:
        raise ValueError(
            f"'{authority}' is not a valid input for the funcion."
            f" Try one in the following list ['canton', 'commune']"
        )
    
    sel = clean_scales(canton, type_of_tax, latest_year).filter(
            pl.col('tax_authority').str.strip_chars()
            .is_in(TAX_AUTHORITIES[authority])
    )
    if len(sel) == 0:
        authorities = ['canton', 'commune', 'federal']
        authorities.remove(authority)
        sel = clean_scales(canton, type_of_tax, latest_year).filter(
            pl.col('tax_authority').str.strip_chars()
            .is_in(TAX_AUTHORITIES[authorities[0]])
        )
    
    sel2 = sel.filter(
        pl.col('taxable_entity').str.strip_chars()
        .is_in(TAXABLE_ENTITIES[taxable_entity])
    )
    if len(sel2) == 0:
        taxable_entity = 'all'
        sel2 = sel.filter(
            pl.col('taxable_entity').str.strip_chars()
            .is_in(TAXABLE_ENTITIES[taxable_entity])
        )

    return sel2

@lru_cache
def calculate_tax_base(net_worth: float, canton: str, **kwargs) -> float: # in progress
    """WARNING!!! There is a eval function below which is better not to use!"""
    scales = select_scales(
        canton, 
        taxable_entity = kwargs.get('taxable_entity', 'single'), 
        type_of_tax = kwargs.get('type_of_tax', 'income'),
        authority = kwargs.get('authority', 'canton'),
        latest_year = kwargs.get('latest_year', datetime.today().year)
    )

    calculation_method = scales.columns[-1]
    if calculation_method == 'base_amount_CHF':
        if max(scales.get_column('base_amount_CHF')) != 0:
            row = scales.filter(pl.col('taxable_worth') <= net_worth).to_dicts()[-1]
            base = row['base_amount_CHF']
            increment = row['additional_percentage'] * (net_worth - row['taxable_worth'])
        else:
            base = 0
            i = 0
            amounts = scales.get_column('taxable_worth')
            factors = scales.get_column('additional_percentage')
            while i < len(amounts)-1 and amounts[i+1] <= net_worth:
                step = amounts[i+1]-amounts[i]
                base += step * factors[i]
                i += 1
            increment = (net_worth - amounts[i]) * factors[i]
        # print(base, increment)
        return base + increment
    
    if calculation_method == 'additional_percentage':
        scales = scales.with_columns(
            taxable_worth = pl.col('to_next_CHF').cum_sum().shift(fill_value=0),
            base_amount_CHF = (
                (pl.col('to_next_CHF') * pl.col('additional_percentage'))
                .cum_sum().shift(fill_value=0)
            ),
        )
        row = scales.filter(pl.col('taxable_worth') <= net_worth).to_dicts()[-1]
        base = row['base_amount_CHF']
        increment = row['additional_percentage'] * (net_worth - row['taxable_worth'])
        return base + increment
    
    if calculation_method == 'tax_rate':
        return scales[0, 'tax_rate'] * net_worth
    
    if calculation_method == 'formula':
        row = scales.filter(pl.col('taxable_worth') <= net_worth).to_dicts()[-1]
        formula: str | None = row['formula']
        # print(formula)
        if formula:
            return eval(formula.replace('$wert$', f'({net_worth})'))
        else:
            return 0

def fill_taxes(net_worth: float):
    table = clean_rates()
    return (
        table.with_columns(
            cantonal_income_tax = (
                pl.col('income_canton')
                * pl.col('canton').map_elements(
                    lambda x: calculate_tax_base(net_worth, x, authority='canton'),
                    pl.Float64
                )
            ),
            communal_income_tax = (
                pl.col('income_commune')
                * pl.col('canton').map_elements(
                    lambda x: calculate_tax_base(net_worth, x, authority='commune'),
                    pl.Float64
                )
            ),
            cantonal_assets_tax = (
                pl.col('assets_canton')
                * pl.col('canton').map_elements(
                    lambda x: calculate_tax_base(
                        net_worth, x, 
                        authority='canton', 
                        type_of_tax = 'assets'
                    ),
                    pl.Float64
                )
            ),
            communal_assets_tax = (
                pl.col('assets_commune')
                * pl.col('canton').map_elements(
                    lambda x: calculate_tax_base(
                        net_worth, x, 
                        authority = 'commune',
                        type_of_tax = 'assets'
                    ),
                    pl.Float64
                )
            ),
            federal_tax = calculate_tax_base(net_worth, 'Conf', authority='federal')
        )
        .with_columns(
            income_tax = (
                pl.col('cantonal_income_tax')
                + pl.col('communal_income_tax')
            ),
            assets_tax = (
                pl.col('cantonal_assets_tax')
                + pl.col('communal_assets_tax')
            ),
            total = (
                pl.col('cantonal_income_tax')
                + pl.col('communal_income_tax')
                + pl.col('cantonal_assets_tax')
                + pl.col('cantonal_assets_tax')
                + pl.col('federal_tax')
            )
        )
    )

@lru_cache
def fill_all_taxes(income: float, assets: float) -> pl.DataFrame:
    table_income = fill_taxes(income)
    table_assets = fill_taxes(assets)
    return (
        table_income.select(
            pl.col('canton_ID'), pl.col('canton'),
            pl.col('FSO_ID'), pl.col('commune'),
            pl.col('federal_tax'), pl.col('income_tax')
        )
        .join(
            table_assets.select(pl.col('FSO_ID'), pl.col('assets_tax')),
            on = 'FSO_ID'
        )
        .with_columns(
            total = pl.col('income_tax') + pl.col('assets_tax')
        )
    )


def show_taxes(income: float, assets:float) -> None:
    table = fill_all_taxes(income, assets)
    print(table.sort(by=pl.col('total'), nulls_last=True))


def _print_rates_table() -> None:
    table = pl.read_excel(
        "data/rates/estv_rates_2023.xlsx",
        has_header=False, engine='xlsx2csv'
    )
    table = table.drop(cs.last())
    table.columns = COLNAMES_RATES
    table = table.slice(4)
    print(table)

def _print_scales_table(canton: str, type_of_tax = 'income', year=2024) -> None:
    table = pl.read_excel(
        f"data/scales/{type_of_tax}/{year}/estv_scales_{canton}.xlsx",
        has_header=False, engine='xlsx2csv'
    )
    table = table.drop(cs.last()).drop(cs.last()).drop(cs.last())
    # table.columns = COLNAMES_SCALES_BASE
    table = table.slice(4)
    not_null_cols = filter(lambda x: x.null_count() != table.height, table)
    not_null_col_names = map(lambda x: x.name, not_null_cols)
    table = table.select(not_null_col_names)
    print(table)

if __name__ == '__main__':
    show_taxes(60_000, 60_000)