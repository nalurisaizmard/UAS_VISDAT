import pandas as pd
df = pd.read_excel('PGCB_date_power_demand.xlsx')
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
print(df[['generation_mw','demand_mw','load_shedding','gas','coal']].describe())
print('\nNilai unik generation_mw (terbesar 10):')
print(sorted(df['generation_mw'].unique())[-10:])
print('\nNilai unik demand_mw (terbesar 10):')
print(sorted(df['demand_mw'].unique())[-10:])