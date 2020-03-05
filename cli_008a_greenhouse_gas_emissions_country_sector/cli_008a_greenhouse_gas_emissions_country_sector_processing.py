import pandas as pd

#pull from url or api instead of local file download
data_loc = '/home/amsnyder/Downloads/historical_emissions.csv'

df = pd.read_csv(data_loc)


df_melt = df.melt(id_vars=['Country', 'Data source', 'Sector', 'Gas', 'Unit'],
        var_name="year",
        value_name="value")

final_df = df_melt.pivot_table('value', ['Country', 'Data source', 'Gas', 'Unit', 'year'], 'Sector').reset_index(level=['Country', 'Data source', 'Gas', 'Unit', 'year'])
final_df.to_csv('/home/amsnyder/Downloads/cli_008a_greenhouse_gas_emissions_country_sector.csv', index=False)

#upload to carto instead of save