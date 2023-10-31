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