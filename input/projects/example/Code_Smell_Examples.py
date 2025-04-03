import pandas as pd
import numpy as np
import tensorflow as tf
import torch
import torch.nn.functional as F

"""
def chain_index_example():
    df = pd.DataFrame([[1, 2, 3], [4, 5, 6]])
    col = 1
    x = 0
    df[col][x] = 42
    df.loc[x, col] = 42


def dataframe_conversion_api_misused_example():
    index = [1, 2, 3, 4, 5, 6, 7]
    a = [np.nan, np.nan, np.nan, 0.1, 0.1, 0.1, 0.1]
    b = [0.2, np.nan, 0.2, 0.2, 0.2, np.nan, np.nan]
    c = [np.nan, 0.5, 0.5, np.nan, 0.5, 0.5, np.nan]
    df = pd.DataFrame({'A': a, 'B': b, 'C': c}, index=index)
    df = df.rename_axis('ID')
    arr = df.values


def matrix_mul_example():
    a = [[1, 0], [0, 1]]
    b = [[4, 1], [2, 2]]
    np.dot(a, b)


def tensor_example(n):
    a = tf.constant(1)
    b = tf.constant(1)
    c = tf.constant([1, 1])
    c = tf.TensorArray(tf.int32, n)
    c = c.write(0, a)
    c = c.write(1, b)
    for i in range(2, n):
        a, b = b, a + b
        c = tf.concat([c, [b]], 0)
        c = c.write(i, b)
        return c


def pytorch_call_method_misused_example(self, x):
    x = self.pool.forward(F.relu(self.conv1(x)))
    x = self.pool(F.relu(self.conv1(x)))
    x = self.pool(F.relu(self.conv2(x)))
        #x = torch.flatten(x, 1) # flatten all dimensions except batch
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc2(x))
    x = self.fc3(x)
    return x


def deterministic_example():
    torch.use_deterministic_algorithms(False)


def merge_api_parameter_not_explicitly_set_example():
    df1 = pd.DataFrame({'key': ['foo', 'bar', 'baz', 'foo'],
                        'value': [1, 2, 3, 5]})
    df2 = pd.DataFrame({'key': ['foo', 'bar', 'baz', 'foo'],
                        'value': [5, 6, 7, 8]})
    df3 = df1.merge(df2)


def columns_and_datatype_not_explicitly_set_example():
    df = pd.read_csv('data.csv')


def empty_example():
    df = pd.DataFrame([])
    df['new_col_int'] = 0
    df['new_col_str'] = ''


def nan_equivalence_example():
    import numpy as np
    df = pd.DataFrame([1, None, 3])
    df_is_nan = df == np.nan


def in_place_example():
    import pandas as pd
    df = pd.DataFrame([-1])
    df.abs()
    df = df.abs()

    ### NumPy
    import numpy as np
    zhats = [2, 3, 1, 0]
    np.clip(zhats, -1, 1)
    zhats = np.clip(zhats, -1, 1)

"""


def in_place_example():
    import pandas as pd

    df = pd.DataFrame([-1])
    df.abs()
    df = df.abs()

    ### NumPy
    import numpy as np

    zhats = [2, 3, 1, 0]
    np.clip(zhats, -1, 1)
    zhats = np.clip(zhats, -1, 1)


def Memory_not_Freed():
    for _ in range(100):
        # tf.keras.backend.clear_session()
        model = tf.keras.Sequential(
            [tf.keras.layers.Dense(10) for _ in range(10)]
        )


def nan_equivalence_example():
    import numpy as np

    df = pd.DataFrame([1, None, 3])
    df_is_nan = df == np.nan


def empty_example():
    df = pd.DataFrame([])
    df["new_col_int"] = 0
    df["new_col_str"] = ""


def merge_api_parameter_not_explicitly_set_example():
    df1 = pd.DataFrame(
        {"key": ["foo", "bar", "baz", "foo"], "value": [1, 2, 3, 5]}
    )
    df2 = pd.DataFrame(
        {"key": ["foo", "bar", "baz", "foo"], "value": [5, 6, 7, 8]}
    )
    df3 = df1.merge(df2)


def columns_and_datatype_not_explicitly_set_example():
    df = pd.read_csv("data.csv")


def deterministic_example():
    torch.use_deterministic_algorithms(True)


def pytorch_call_method_misused_example(self, x):
    x = self.pool.forward(F.relu(self.conv1(x)))
    x = self.pool(F.relu(self.conv1(x)))
    x = self.pool(F.relu(self.conv2(x)))
    # x = torch.flatten(x, 1) # flatten all dimensions except batch
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc2(x))
    x = self.fc3(x)
    return x


def tensor_example(n):
    a = tf.constant(1)
    b = tf.constant(1)
    c = tf.constant([1, 1])
    c = tf.TensorArray(tf.int32, n)
    c = c.write(0, a)
    c = c.write(1, b)
    for i in range(2, n):
        a, b = b, a + b
        c = tf.concat([c, [b]], 0)
        c = c.write(i, b)
        return c


def matrix_mul_example():
    a = [[1, 0], [0, 1]]
    b = [[4, 1], [2, 2]]
    np.dot(a, b)


def dataframe_conversion_api_misused_example():
    index = [1, 2, 3, 4, 5, 6, 7]
    a = [np.nan, np.nan, np.nan, 0.1, 0.1, 0.1, 0.1]
    b = [0.2, np.nan, 0.2, 0.2, 0.2, np.nan, np.nan]
    c = [np.nan, 0.5, 0.5, np.nan, 0.5, 0.5, np.nan]
    df = pd.DataFrame({"A": a, "B": b, "C": c}, index=index)
    df = df.rename_axis("ID")
    arr = df.values


def chain_index_example():
    df = pd.DataFrame([[1, 2, 3], [4, 5, 6]])
    col = 1
    x = 0
    df[col][x] = 42
    df.loc[x, col] = 42


def pandas_lib_check():
    x = pd.DataFrame([1, 2, 3])
    y = x
    z = x.concat(y)
    c = x["ciao"]
    d = x["ciao"].values
