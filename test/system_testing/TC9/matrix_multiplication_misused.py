import numpy as np


def matrix():
    # Matrici costanti
    matrix_a = [[1, 2], [3, 4]]
    matrix_b = [[5, 6], [7, 8]]

    # Uso scorretto di `np.dot`
    result = np.dot(matrix_a, matrix_b)  # Punto di rilevamento # noqa
