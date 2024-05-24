
import pandas as pd
import numpy as np

def split_and_expand(df, column_name):
    df[column_name] = df[column_name].str.split(' - ')
    df_expanded = df.explode(column_name)
    return df_expanded

def clean(input):
    input['Debitore'] = input['Debitore'].str.strip()

    input = split_and_expand(input, 'N° Rep PPT')
    input['N. RG'] = (input['N. RG'].str.replace('Rg.', '', regex=False)
                    .str.replace('Nr.', '', regex=False)
                    .str.replace('-', '/', regex=False)
                    .str.strip()
                    )
    input['N. Decreto'] = (input['N. Decreto'] .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('-', '/', regex=False)
                            .str.strip()
                        )
    input['N° Repertorio'] = (input['N° Repertorio'] .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('-', '/', regex=False)
                            .str.strip()
                        )
    input['N. Cronologico'] = (input['N. Cronologico'] .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('-', '/', regex=False)
                            .str.strip()
                        )
    input['N.R.G.E PPT'] = (input['N.R.G.E PPT'] .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('-', '/', regex=False)
                            .str.strip()
                        )
    input['N° Rep PPT'] = (input['N° Rep PPT'] .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            # .str.replace('-', '/', regex=False)
                            .str.strip()
                        )

    input[['nr.rg', 'year.rg']] = input['N. RG'].str.split('/', expand=True)
    input[['nr.decreto', 'year.decreto']] = input['N. Decreto'].str.split('/', expand=True)
    input[['nr.repertorio', 'year.repertorio']] = input['N° Repertorio'].str.split('/', expand=True)
    input[['nr.crono', 'year.crono']] = input['N. Cronologico'].str.split('/', expand=True)
    input[['nr.rgeppt', 'year.rgeppt']] = input['N.R.G.E PPT'].str.split('/', expand=True)
    input[['nr.repppt', 'year.repppt']] = input['N° Rep PPT'].str.split('/', expand=True)
    input['tipo_ricerca'] = input['RICERCA IQERA'].str.lower()
    input = input.drop(columns=['N. RG','N. Decreto','N° Repertorio','N. Cronologico','N.R.G.E PPT','N° Rep PPT','RICERCA IQERA'])

    def update_year(year):
        if pd.isna(year):
            return year
        year = int(year)

        if year < 100:
            if 0 <= year <= 24:
                return 2000 + int(year)
            else:
                return 1900 + int(year)
        return (year)

    # List of columns to update
    year_columns = [col for col in input.columns if col.startswith('year')]

    # Apply the function to the relevant columns
    for col in year_columns:
        input[col] = input[col].apply(update_year)
        input[col] = input[col].astype(str).str.split('.').str[0]

    input.replace('nan', np.nan, inplace=True)

    return input

