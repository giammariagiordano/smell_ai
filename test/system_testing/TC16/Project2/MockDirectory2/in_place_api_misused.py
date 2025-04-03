import pandas as pd


def misuse_inplace_api():
    df = pd.DataFrame({"col": [1, 2, None]})
    df.fillna(0, inplace=True)  # Smell: inplace=True usato
    return df
