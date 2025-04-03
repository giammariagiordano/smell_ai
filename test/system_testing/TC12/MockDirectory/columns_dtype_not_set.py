import pandas as pd


def columns_and_datatype_not_explicitly_set_example():
    df = pd.read_csv("data.csv")  # noqa


def load_data(file_path):
    df = pd.read_csv(file_path)  # Manca esplicitazione di `dtype`
    return df
