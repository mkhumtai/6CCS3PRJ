import pandas as pd
pd.options.mode.chained_assignment = None

def find_species_and_types(speciesDec):
    """ Returns species type and species from the column speciesDescription

    Parameters:
        speciesDec (list): A list containing the species and its type e.g. wild goose

    Returns:
        types, ', '.join(species) (list): Returns a list of a cleaned column

    """
    types = []

    if type(speciesDec) == float:
        sd = None
    else:
        sd = speciesDec.split(',')

    if sd is None:
        types.append('human')
    else:
        for s in sd:
            if 'wild' in s:
                types.append('wild')
            if 'domestic' in s:
                types.append('domestic')
            if 'captive' in s:
                types.append('captive')

    types = list(set(types))
    species = []
    if type(speciesDec) != float:
        for sp in sd:
            sp = sp.lstrip()
            if sp not in types and sp != 'environmental sample':
                species.append(sp)
    else:
        species.append('human')
    types = ", ".join(types)
    return types, ', '.join(species)


def clean_df(df):
    """ Cleans the dataframe by removing unwanted columns, adding additional columns and
        changing column type

        Parameters:
            df (df): A dataframe from imported .csv file

        Returns:
            empres_df (df): Returns a list of a cleaned column

    """

    # Only use data with confirmed status
    df = df[df.status == 'Confirmed']

    # Delete status and disease as it's always 'Confirmed' and 'Avian Influenza'
    del df['status']
    del df['disease']

    # swap ordering of the dates
    df['observationDate'] = pd.to_datetime(df['observationDate'], format='%d/%m/%Y', errors='ignore')
    df['reportingDate'] = pd.to_datetime(df['reportingDate'], format='%d/%m/%Y', errors='ignore')

    # Add quarters column
    df['quarters'] = pd.PeriodIndex(pd.to_datetime(df.reportingDate), freq='Q').astype(str)

    # Replace single quotes with blank space
    df['localityName'] = df['localityName'].apply(lambda s: s.replace("'", " "))
    df['admin1'] = df['admin1'].apply(lambda s: s.replace("'", " "))
    df['country'] = df['country'].apply(lambda s: s.replace("'", " "))
    df['localityQuality'] = df['localityQuality'].apply(lambda s: s.replace("'", " "))

    # Reorder dataframe
    df = df[['source', 'latitude', 'longitude', 'region', 'country', 'admin1',
             'localityName', 'localityQuality', 'observationDate', 'reportingDate', 'quarters', 'serotypes',
             'speciesType', 'species',
             'sumAtRisk', 'sumCases', 'sumDeaths', 'sumDestroyed', 'sumSlaughtered',
             'humansGenderDesc', 'humansAge', 'humansAffected', 'humansDeaths']]

    return df
