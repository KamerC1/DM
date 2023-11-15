import pandas as pd
import numpy as np

def get_converted_incidents_df(incidents_path = '../../data/incidents.csv') -> pd.DataFrame:
    """
    Ritorna il dataframe con i dati convertiti. Se nei dati numerici ci sono delle stringhe, questi vengono rimossi.
    Tutti i numeri naturali con valori NaN son stati convertiti in Float64 perché il tipo Int64 non supporta i NaN.
    """
    
    dtype={
        'state': 'string',
        'city_or_county': 'string',
        'address': 'string',
        'latitude': 'float64',
        'longitude': 'float64',
        'congressional_district': 'Int64',
        'state_house_district': 'Int64',
        'state_senate_district': 'Int64',
        'participant_age1': 'Int64',
        'participant_age_group1': 'string',
        'participant_gender1': 'string',
        'n_males': 'float64',
        'n_females': 'float64',
        'n_killed': 'int64',
        'n_injured': 'int64',
        'n_arrested': 'float64',
        'n_unharmed': 'float64',
        'n_participants': 'float64',
        'n_arrested': 'float64',
        'notes': 'string',
        'incident_characteristics1': 'string',
        'incident_characteristics2': 'string'}

    df = pd.read_csv(incidents_path, sep=',', low_memory=False, dtype=dtype)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    #Eliminazione dati con tipo string e conversione in float64
    df['min_age_participants'] = pd.to_numeric(df['min_age_participants'], errors='coerce')
    df['avg_age_participants'] = pd.to_numeric(df['avg_age_participants'], errors='coerce')
    df['max_age_participants'] = pd.to_numeric(df['max_age_participants'], errors='coerce')
    df['n_participants_child'] = pd.to_numeric(df['n_participants_child'], errors='coerce')
    df['n_participants_teen'] = pd.to_numeric(df['n_participants_teen'], errors='coerce')
    df['n_participants_adult'] = pd.to_numeric(df['n_participants_adult'], errors='coerce')
    
    return df


def get_merged_df(incidents_df_path: str = '../../data/incidents.csv', poverty_df_path: str = '../../data/povertyByStateYear.csv') -> pd.DataFrame:
        """
        Esegue left join tra i due dataset e ritorna il dataframe risultante (left join eseguita su year e state).
        """

        poverty_df = poverty_converted(poverty_df_path)
        incidents_df = get_converted_incidents_df(incidents_df_path)

        #Controllo se ci sono stati che non sono presenti in entrambi i dataset
        state_poverty_s = pd.Series(poverty_df.state.unique())
        state_incidents_s = pd.Series(incidents_df.state.unique())
        assert (~state_incidents_s.isin(state_poverty_s)).sum() == 0

        incidents_df['year'] = incidents_df['date'].dt.year
        merged_df = pd.merge(incidents_df, poverty_df, on=['year', 'state'], how='left').drop(columns=['year'])

        assert len(merged_df) == len(incidents_df)

        return merged_df
    
def poverty_converted(povertyByStateYear_path: str = '../../data/povertyByStateYear.csv') -> pd.DataFrame:
    poverty_dtype={
            'state': 'string',
            'year': 'int64',
            'povertyPercentage': 'float64'
    }

    return pd.read_csv(povertyByStateYear_path, sep=',', dtype=poverty_dtype)

    
def povertyImprovment(povertyByStateYear_path: str = '../../data/povertyByStateYear.csv') -> pd.DataFrame:
    """
    Gestisce valori sbagliati, nulli e mancanti del dataset povertyByStateYear.csv e ritorna il dataframe risultante.
    
    Il datafreame povertyByStateYear:
        - contiene valori null per il campo 2012 => calcola la media tra 2011 e 2013 in base allo stato
        - coppia <Wyoming, 2009> compare due volte con valori diversi per povertyPercentage => sostituisci con la media
        - coppia <Wyoming, 2010> non compare => aggiungi una riga con la media tra 2009 e 2011
    Per riempire questi valori nulli, si è deciso di calcolare la media tra i valori del campo 2011 e 2013 in baso allo stato.
    """
    
    poverty_dtype={
            'state': 'string',
            'year': 'int64',
            'povertyPercentage': 'float64'
    }

    df = pd.read_csv(povertyByStateYear_path, sep=',', dtype=poverty_dtype)
    
    #coppia <Wyoming, 2009> compare due volte con valori diversi per povertyPercentage => sostituisci con la media
    mean_value = df[(df.state == "Wyoming") & (df.year == 2009)].povertyPercentage.mean()
    df.drop_duplicates(inplace=True, subset=['state', 'year'])
    df.loc[(df.state == "Wyoming") & (df.year == 2009), 'povertyPercentage'] = mean_value
    
    
    #Coppia <Wyoming, 2010> non compare => aggiungi una riga con la media tra 2009 e 2011
    povertyPercentage_2009 = df[(df.state == "Wyoming") & (df.year == 2009)].povertyPercentage.values[0]
    povertyPercentage_2011 = df[(df.state == "Wyoming") & (df.year == 2011)].povertyPercentage.values[0]
    mean_povertyPercentage = (povertyPercentage_2009 + povertyPercentage_2011) / 2

    new_entry = pd.DataFrame({'state': ['Wyoming'], 'year': [2010], 'povertyPercentage': [mean_povertyPercentage]})
    df.append(new_entry, ignore_index=True)
    
    
    #Il campo 2012 è vuoto => calcola la media tra 2011 e 2013 in base allo stato
    df_2013 = df[df['year'] == 2013]
    df_2011 = df[df['year'] == 2011]

    #Calcola media povertyPercentage tra 2013 e 2011 in base allo stato
    merged = pd.merge(df_2013, df_2011, on='state', suffixes=('_2013', '_2011')).drop(columns=['year_2013', 'year_2011'])
    merged['povertyPercentage_2012'] = (merged['povertyPercentage_2013'] + merged['povertyPercentage_2011']) / 2
    merged = merged.drop(columns=['povertyPercentage_2013', 'povertyPercentage_2011'])

    #Sostiuisci i valori dell'anno 2012 con la media calcolata (NB tutti i valori )
    merge_df = pd.merge(df, merged, on="state", how="left", suffixes=('', '_2012'))
    merge_df['povertyPercentage'] = merge_df['povertyPercentage'].fillna(merge_df['povertyPercentage_2012'])
    
    return merge_df.drop(columns=['povertyPercentage_2012'])