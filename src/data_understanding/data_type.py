import pandas as pd
import matplotlib.pyplot as plt


def get_converted_incidents_df(incidents_path = '../../data/incidents.csv'):
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
    df['n_participants_adult'] = pd.to_numeric(df['n_participants_teen'], errors='coerce')
    
    return df


def get_merged_df(incidents_df_path: str = '../../data/incidents.csv', poverty_df_path: str = '../../data/povertyByStateYear.csv') -> pd.DataFrame:
        """
        Esegue left join tra i due dataset e ritorna il dataframe risultante (left join eseguita su year e state).
        """

        poverty_dtype={
                'state': 'string',
                'year': 'int64',
                'povertyPercentage': 'float64'
        }

        poverty_df = pd.read_csv(poverty_df_path, sep=',', dtype=poverty_dtype)
        incidents_df = get_converted_incidents_df(incidents_df_path)

        #Controllo se ci sono stati che non sono presenti in entrambi i dataset
        state_poverty_s = pd.Series(poverty_df.state.unique())
        state_incidents_s = pd.Series(incidents_df.state.unique())
        assert (~state_incidents_s.isin(state_poverty_s)).sum() == 0

        incidents_df['year'] = incidents_df['date'].dt.year
        merged_df = pd.merge(incidents_df, poverty_df, on=['year', 'state'], how='left').drop(columns=['year'])

        assert len(merged_df) == len(incidents_df)

        return merged_df