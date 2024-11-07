import os

import polars as pl
import polars.selectors as cs

from icecream import ic

table = pl.read_excel("data/rates/estv_rates_2023.xlsx",
                      has_header=False, engine='xlsx2csv')
table = table.drop(cs.last())

COLNAMES = [
    'canton_ID', 'canton', 'FSO_ID', 'commune', 
    'income_canton', 'income_commune',
    'income_protestant', 'income_roman', 'income_catholic',
    'assets_canton', 'assets_commune',
    'assets_protestant', 'assets_roman', 'assets_catholic',
    'profit_canton', 'profit_commune', 'profit_church',
    'capital_canton', 'capital_commune', 'capital_church'
]

table.columns = COLNAMES
table = table.slice(4)


def find_multipliers(rates_df: pl.DataFrame, 
                     commune: str) -> None | dict[str | float]:
    # commune = commune.lower()
    multipliers = (
        rates_df.filter(pl.col("commune")
                .str.contains(commune, literal=True))
    )
    # print(multipliers.to_dicts()[0])
    multipliers = (
        multipliers.select(
            pl.col('canton_ID', 'canton', 'FSO_ID', 'commune'),
            pl.all()
              .exclude('canton_ID', 'canton', 'FSO_ID', 'commune')
              .cast(pl.Float64) / 100
          )
          .to_dicts()
    )
    return None if len(multipliers) == 0 else multipliers[0]

def find_multipliers_by_year(commune: str, 
                             latest_year: int = 2024) -> tuple[dict[str | float] | int]:
    file_path = f"data/rates/estv_rates_{latest_year}.xlsx"
    multipliers = None
    while os.path.exists(file_path) and multipliers is None:
        rates = pl.read_excel(
            f"data/rates/estv_rates_{latest_year}.xlsx",
            has_header=False, 
            engine='xlsx2csv'
        )
        rates = rates.drop(cs.last())
        rates.columns = COLNAMES
        multipliers = find_multipliers(rates, commune)
        latest_year -= 1
    return multipliers, latest_year + 1     
    

if __name__ == '__main__':
    print(table)
    print(find_multipliers(table, 'Adliswil'))
    print(find_multipliers_by_year('Lugano'))