import pandas as pd


def dataframe_conversion_api_misused():
    data = {"A": [1, 2, 3], "B": [4, 5, 6]}
    df = pd.DataFrame(data)

    # Uso scorretto di `.values`
    array = df.values  # Punto di rilevamento # noqa
