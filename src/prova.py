import pandas as pd

table = pd.read_excel("data/rates/estv_rates_2023.xlsx", header=3)
print(
    table.loc[table['Comune'] == 'Lugano']
)
# col_names = table.row(3)

# def find_multipliers(rates_df: pl.DataFrame, wealth_source: str, commune: str) -> tuple[float | float]:
#     assert wealth_source in ['income', 'assets']
#     multipliers = (
#     rates_df.select(
#         pl.col('column_4'),
#         pl.col('column_5'),
#         pl.col('column_6')
#     )
#     .filter(pl.col("column_4").str.contains(commune, literal=True))
#     )
#     print(multipliers)
#     return (
#         multipliers.select(
#             pl.col('column_5')                 
#               .str.to_decimal()/100,
#             pl.col('column_6')                 
#               .str.to_decimal()/100,
#         )[0].transpose().to_series().to_list()
#     )


# def find_multiplier_by_year(canton: str, year: int = 2023) -> tuple[float | float]:
#     table = pl.read_excel(f"scales/assets/{year}/")

# table.find_multiplier = MethodType(find_multiplier, table)



# if __name__ == '__main__':
#     print(table)
#     print(table.columns)
    # print(col_names)
    # print(*find_multipliers(table, 'income', 'Lugano'))