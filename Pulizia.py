
import pandas as pd
import numpy as np

def split_and_expand(df, column_name):
    if df[column_name].notna().any():
        df[column_name] = df[column_name].str.split(' - ')
        df_expanded = df.explode(column_name)
        return df_expanded
    else:
        return df

def process_values(value):
    if isinstance(value, float) and np.isnan(value):
        return value
    if '-' in value and '/' in value:
        return value
    elif '-' in value:
        return value.replace('-', '/')
    else:
        return value

def process_column(column):
    return column.apply(process_values)

def split_and_expand_columns(df, columns):
    for column_name in columns:
        print(column_name)
        df[column_name] = process_column(df[column_name])
        df = split_and_expand(df, column_name)
    return df

def clean(input):

    input.replace('nan', np.nan, inplace=True)

    values_to_replace = ['Da Ricercare', 'NO DISP. BSS', '[Da Ricercare]']

    """    input['N. RG'].replace(values_to_replace, np.nan, inplace=True)
    input['N. Decreto'].replace(values_to_replace, np.nan, inplace=True)
    input['N° Repertorio'].replace(values_to_replace, np.nan, inplace=True)
    input['N. Cronologico'].replace(values_to_replace, np.nan, inplace=True)
    input['N.R.G.E PPT'].replace(values_to_replace, np.nan, inplace=True)
    input['N° Rep PPT'].replace(values_to_replace, np.nan, inplace=True)"""

    for col in input.columns:
        if col.startswith('N'):
            input[col].replace(values_to_replace, np.nan, inplace=True)
    
    input['Debitore'] = input['Debitore'].str.strip()

    # input = split_and_expand(input, 'N° Rep PPT')
    columns_to_process = [col for col in input.columns if col.startswith('N')]
    columns_to_process.remove('NR_Contratto')
    
    # input = split_and_expand_columns(input, columns_to_process)

    if input['N. RG'].notna().any():
        input['N. RG'] = (input['N. RG'].str.replace('Rg.', '', regex=False)
                    .str.replace('Nr.', '', regex=False)
                    .str.replace('N.', '', regex=False)
                    .str.strip()
                    )
        split_result = input['N. RG'].str.split('/', expand=True)
        # Handling inconsistent split results
        if split_result.shape[1] == 2:
            input[['nr.rg', 'year.rg']] = split_result
        else:
            print("Split did not produce the expected number of columns for some rows.")
            # Handle the case here, e.g., by filling NaNs
            split_result = split_result.reindex(columns=[0, 1]).fillna('')
            input[['nr.rg', 'year.rg']] = split_result
        
    if input['N. Decreto'].notna().any():
        input['N. Decreto'] = (input['N. Decreto'] 
                            .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('N.', '', regex=False)
                            .str.strip()
                        )
        
        split_result = input['N. Decreto'].str.split('/', expand=True)
        # Handling inconsistent split results
        if split_result.shape[1] == 2:
            input[['nr.decreto', 'year.decreto']] = split_result
        else:
            print("Split did not produce the expected number of columns for some rows.")
            # Handle the case here, e.g., by filling NaNs
            split_result = split_result.reindex(columns=[0, 1]).fillna('')
            input[['nr.decreto', 'year.decreto']] = split_result
        # input[['nr.decreto', 'year.decreto']] = input['N. Decreto'].str.split('/', expand=True)
        
    if input['N° Repertorio'].notna().any():
        input['N° Repertorio'] = (input['N° Repertorio'] .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('N.', '', regex=False)
                            .str.strip()
                        )
        input[['nr.repertorio', 'year.repertorio']] = input['N° Repertorio'].str.split('/', expand=True)

    if input['N. Cronologico'].notna().any():
        input['N. Cronologico'] = (input['N. Cronologico'] .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('N.', '', regex=False)
                            .str.strip()
                        )
        split_result = input['N. Cronologico'].str.split('/', expand=True)
        if split_result.shape[1] == 2:
            input[['nr.crono', 'year.crono']] = split_result
        else:
            print("Split did not produce the expected number of columns for some rows.")
            # Handle the case here, e.g., by filling NaNs
            split_result = split_result.reindex(columns=[0, 1]).fillna('')
            input[['nr.crono', 'year.crono']] = split_result
        
    if input['N.R.G.E PPT'].notna().any():
        input['N.R.G.E PPT'] = (input['N.R.G.E PPT'] 
                            .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.replace('N.', '', regex=False)
                            .str.strip()
                        )
        input[['nr.rgeppt', 'year.rgeppt']] = input['N.R.G.E PPT'].str.split('/', expand=True)
    
    if input['N° Rep PPT'].notna().any():
        input['N° Rep PPT'] = (input['N° Rep PPT'] 
                            .str.replace('N.', '', regex=False)
                            .str.replace('Nr.', '', regex=False)
                            .str.replace('Rg.', '', regex=False)
                            .str.strip()
                        )
        input[['nr.repppt', 'year.repppt']] = input['N° Rep PPT'].str.split('/', expand=True)

    input['tipo_ricerca'] = input['RICERCA IQERA'].str.lower()
    input = input.drop(columns=['N. RG','N. Decreto','N° Repertorio','N. Cronologico','N.R.G.E PPT','N° Rep PPT','RICERCA IQERA'])

    def update_year(year):
        if pd.isna(year) or year=='':
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

