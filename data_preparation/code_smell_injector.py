import random
from data_preparation.base_llm import BaseLLM


class CodeSmellInjector:
    """
    A class to inject code smells into clean Python
    functions using a language model (LLM).
    """

    def __init__(self, llm_model: BaseLLM, max_smells=2):
        """
        Initializes the CodeSmellInjector.

        Args:
            llm_model (BaseLLM): An instance of a language
            model used for code generation.
            max_smells (int): Maximum number of code smells to
            inject per function (default is 2).
        """
        self.llm_model = llm_model  # Instance of a language model
        self.max_smells = max_smells

        # Equal distribution of code smells with descriptions and examples
        self.smell_descriptions = {
            "Broadcasting Feature Not Used": {
                "description": (
                    "This smell occurs when a developer uses explicit "
                    "tiling or tensor operations without "
                    "leveraging broadcasting, a TensorFlow feature "
                    "that efficiently manipulates tensors "
                    "without requiring explicit replication of data."
                ),
                "example": (
                    """
                    import tensorflow as tf

                    # Example 1: Explicit tiling instead of broadcasting
                    def combine_tensors(tensor_b, tensor_c):
                        # Code smell: Using explicit tiling to match dimensions
                        tensor_a = tf.tile(tensor_b, [1, 3]) + tensor_c
                        return tensor_a

                    # Suggested fix:
                    # Utilize broadcasting for efficient manipulation
                    # tensor_a = tensor_b + tensor_c

                    # Example 2: Tiling a scalar tensor to match shape
                    scalar = tf.constant(5)
                    matrix = tf.constant([[1, 2], [3, 4]])

                    # Code smell: Explicitly tiling a scalar to
                    # match matrix shape
                    tiled_scalar = tf.tile(tf.expand_dims(
                        tf.expand_dims(scalar, 0), 0), [2, 2]
                    )
                    result = tiled_scalar + matrix

                    # Suggested fix:
                    # Broadcasting can handle scalar
                    # and matrix addition automatically
                    # result = scalar + matrix

                    # Example 3: Element-wise multiplication
                    #  with mismatched shapes
                    tensor1 = tf.constant([[1, 2, 3]])
                    tensor2 = tf.constant([1, 2, 3])

                    # Code smell: Manually reshaping tensors
                    # to enable multiplication
                    reshaped_tensor1 = tf.tile(tensor1, [3, 1])
                    reshaped_tensor2 = tf.tile(
                        tf.expand_dims(tensor2, axis=1), [1, 3]
                    )
                    product = reshaped_tensor1 * reshaped_tensor2

                    # Suggested fix:
                    # Broadcasting automatically resolves shape mismatches
                    # product = tensor1 * tf.expand_dims(tensor2, axis=0)

                    # Example 4: Avoiding broadcasting in a batch operation
                    batch = tf.constant([[1, 2, 3], [4, 5, 6]])
                    scale = tf.constant([2, 3])

                    # Code smell: Expanding and tiling
                    # to match batch dimensions
                    scaled_batch = batch * tf.tile(
                        tf.expand_dims(scale, 0), [batch.shape[0], 1]
                    )

                    # Suggested fix:
                    # Broadcasting can scale batches directly
                    # scaled_batch = batch * scale
                    """
                ),
                "definition": (
                    "This smell refers to when the developer uses "
                    "explicit tiling or tensor expansion operations "
                    "instead of taking advantage of broadcasting, "
                    "which handles shape mismatches efficiently."
                ),
                "rationale": (
                    "Broadcasting reduces memory usage and improves code "
                    "readability by avoiding explicit data replication. "
                    "TensorFlow operations are designed to automatically "
                    "align tensor shapes using broadcasting rules. "
                    "Failing to leverage broadcasting leads to inefficient "
                    "operations, increased memory consumption, "
                    "and complex, error-prone code."
                ),
            },
            "Chain Indexing": {
                "description": (
                    "This smell occurs when chained indexing ([][]) "
                    "is used to access or modify elements in a "
                    "Pandas DataFrame. This practice can lead to "
                    "unpredictable behavior, performance issues, and "
                    "potential bugs, as intermediate copies of the "
                    "data may be created."
                ),
                "example": (
                    """
                    import pandas as pd

                    # Create a sample DataFrame
                    df = pd.DataFrame({
                        'A': [1, 2, 3],
                        'B': [4, 5, 6],
                        'C': [7, 8, 9]
                    })

                    # Example 1: Accessing elements with chained indexing
                    def get_value_with_chained_indexing(df):
                        # Code smell: Chained indexing for accessing a value
                        value = df['A'][0]  # May create an intermediate object
                        return value

                    # Suggested fix:
                    # Use loc for safer and more predictable indexing
                    # value = df.loc[0, 'A']

                    # Example 2: Modifying elements with chained indexing
                    def modify_value_with_chained_indexing(df):
                        # Code smell: Chained indexing for modifying a value
                        df['B'][1] = 10
                        # Risk of modifying a copy
                        # instead of the original DataFrame

                    # Suggested fix:
                    # Use loc or iloc for modifying elements
                    # df.loc[1, 'B'] = 10
                    """
                ),
                "definition": (
                    "This smell refers to accessing or modifying elements "
                    "in a Pandas DataFrame using chained indexing ([][]), "
                    "which is discouraged due to the risk of creating "
                    "intermediate objects and unpredictable behavior."
                ),
                "rationale": (
                    "Chained indexing creates intermediate objects, "
                    "which can result in unintentional behavior "
                    "such as modifying a copy instead of the original "
                    "DataFrame. It can also lead to significant "
                    "performance degradation, particularly "
                    "in large datasets. Using explicit indexing methods "
                    "like loc or iloc ensures safer, more predictable, "
                    "and faster operations."
                ),
            },
            "Columns and DataType Not Explicitly Set": {
                "description": (
                    "This smell occurs when DataFrame columns and "
                    "their data types are not explicitly defined, "
                    "leaving Pandas to infer them automatically. "
                    "This can lead to inconsistencies, unexpected "
                    "type inference, and potential runtime errors, "
                    "especially when working with large or dynamic datasets."
                ),
                "example": (
                    """
                    import pandas as pd

                    # Example 1: Creating a DataFrame without
                    # specifying columns and types
                    def create_dataframe_implicit():
                        # Code smell: Columns and types are not explicitly set
                        data = [[1, 'Alice', 25.5], [2, 'Bob', 30.0]]
                        df = pd.DataFrame(data)
                        # Column names and types are inferred
                        return df

                    # Suggested fix:
                    # Explicitly set column names and types
                    # data = {'ID': [1, 2], 'Name': ['Alice', 'Bob'],
                    # 'Age': [25.5, 30.0]}
                    # df = pd.DataFrame(data)

                    # Example 2: Reading a CSV without specifying types
                    def read_csv_implicit(filepath):
                        # Code smell: Data types are inferred automatically
                        df = pd.read_csv(filepath)  # May infer incorrect types
                        return df

                    # Suggested fix:
                    # Use dtype argument to specify expected types
                    # df = pd.read_csv(filepath, dtype={'ID': int, 'Name': str,
                    # 'Age': float})

                    # Example 3: Modifying a DataFrame ù
                    # without setting types for new columns
                    def add_column_implicit(df):
                        # Code smell: Adding a column without defining its type
                        df['New_Column'] = [1, 2, 3]  # Type is inferred
                        return df

                    # Suggested fix:
                    # Explicitly set the type of the new column
                    # df['New_Column'] = pd.Series([1, 2, 3], dtype='int64')
                    """
                ),
                "definition": (
                    "This smell refers to the creation or "
                    "modification of a DataFrame without explicitly defining "
                    "column names and their corresponding data types, "
                    "relying instead on automatic inference."
                ),
                "rationale": (
                    "Explicitly setting column names and data types "
                    "ensures data consistency, improves code readability, "
                    "and reduces the risk of runtime errors or incorrect "
                    "behavior caused by incorrect type inference. "
                    "It is particularly important when working with "
                    "external data sources (e.g., CSV files) or large, "
                    "dynamic datasets where inferred types "
                    "may vary unexpectedly."
                ),
            },
            "Dataframe Conversion API Misused": {
                "description": (
                    "This smell occurs when `.values` is used to "
                    "convert a Pandas DataFrame to a NumPy array. "
                    "While `.values` may work in many cases, "
                    "it is a legacy method and is less explicit, "
                    "less readable, and potentially prone to "
                    "issues in edge cases. The `.to_numpy()` "
                    "method is the recommended, modern approach, "
                    "aligning with Pandas' design principles and "
                    "ensuring future compatibility."
                ),
                "example": (
                    """
                    import pandas as pd

                    # Example 1: Basic DataFrame conversion
                    def convert_dataframe_to_array(df):
                        # Code smell: Using .values for conversion
                        array = df.values
                        # Discouraged due to readability
                        # and future-proofing concerns
                        return array

                    # Suggested fix:
                    # Use .to_numpy(), which is explicit and recommended
                    # array = df.to_numpy()
                    # return array

                    # Example 2: DataFrame with mixed data types
                    def convert_mixed_type_dataframe(df):
                        # DataFrame with mixed types
                        df = pd.DataFrame({
                            'A': [1, 2, 3],
                            'B': ['x', 'y', 'z']
                        })

                        # Code smell: Using .values can lead
                        # to issues with ExtensionArrays or mixed types
                        array = df.values

                        # Suggested fix:
                        # .to_numpy() handles mixed types more consistently
                        # array = df.to_numpy()

                    # Example 3: Handling nullable
                    #  integer types (Pandas ExtensionArray)
                    def handle_nullable_types(df):
                        # DataFrame with nullable integers
                        df = pd.DataFrame({
                            'A': [1, 2, None],
                            'B': [4, None, 6]
                        })

                        # Code smell: Using .values may produce
                        #  unexpected results with nullable types
                        array = df.values

                        # Suggested fix:
                        # Use .to_numpy() with explicit na_value
                        #  to handle nulls
                        # array = df.to_numpy(dtype='object')

                    # Example 4: Conversion in chained operations
                    def chain_conversion_operations(df):
                        # Code smell: Using .values in a chain
                        result = df.values.sum(axis=0)

                        # Suggested fix:
                        # Use .to_numpy() for clarity and consistency
                        # result = df.to_numpy().sum(axis=0)
                    """
                ),
                "definition": (
                    "This smell refers to converting Pandas "
                    "DataFrames to NumPy arrays using `.values`, "
                    "which is considered a legacy method, "
                    "instead of the recommended `.to_numpy()` approach."
                ),
                "rationale": (
                    "Using `.to_numpy()` over `.values` improves code "
                    "clarity and aligns with Pandas' modern API design. "
                    "The `.values` attribute may lead to unexpected "
                    "behavior in edge cases, particularly with DataFrames "
                    "that include Pandas ExtensionArrays "
                    "(e.g., nullable integers) or mixed data types. "
                    "The `.to_numpy()` method is explicit, "
                    "future-proof, and better handles such scenarios. "
                    "Adopting `.to_numpy()` ensures that the code "
                    "remains robust, readable, and compatible "
                    "with future updates to Pandas and NumPy."
                ),
            },
            "Deterministic Algorithm Option Not Used": {
                "description": (
                    "This smell occurs when the option "
                    "'torch.use_deterministic_algorithms(True)' is set "
                    "and not properly managed or removed after "
                    "its intended use. While this option is "
                    "useful for ensuring reproducibility during "
                    "debugging and validation, leaving it "
                    "enabled unnecessarily can negatively impact "
                    "performance and limit the flexibility "
                    "of machine learning pipelines."
                ),
                "example": (
                    """
                    import torch

                    # Example 1: Setting deterministic
                    # algorithms without disabling later
                    def train_model(model, dataloader, optimizer, loss_fn):
                        # Code smell: Deterministic algorithms
                        # enabled without clear intent or removal
                        torch.use_deterministic_algorithms(True)

                        for epoch in range(10):
                            for inputs, targets in dataloader:
                                optimizer.zero_grad()
                                outputs = model(inputs)
                                loss = loss_fn(outputs, targets)
                                loss.backward()
                                optimizer.step()

                    # Suggested fix:
                    # Use a context manager or explicitly disable
                    #  deterministic algorithms when not needed
                    # with torch.use_deterministic_algorithms(True):
                    #     for epoch in range(10):
                    #         for inputs, targets in dataloader:
                    #             optimizer.zero_grad()
                    #             outputs = model(inputs)
                    #             loss = loss_fn(outputs, targets)
                    #             loss.backward()
                    #             optimizer.step()

                    # Example 2: Enabling deterministic
                    # algorithms globally in production
                    torch.use_deterministic_algorithms(True)
                    # Code smell: Performance degradation likely
                    model = torch.nn.Linear(10, 1)

                    def predict(inputs):
                        return model(inputs)

                    # Suggested fix:
                    # Enable deterministic algorithms
                    # only during debugging or validation
                    # torch.use_deterministic_algorithms(False)

                    # Example 3: Incorrect usage in mixed
                    # deterministic and non-deterministic pipelines
                    def mixed_pipeline():
                        # Code smell: Enabling deterministic
                        # algorithms globally affects
                        # non-deterministic components
                        torch.use_deterministic_algorithms(True)
                        model = torch.nn.Linear(10, 5)

                        # Non-deterministic step: Data augmentation pipeline
                        data = torch.randn(100, 10) * torch.randn(100, 10)
                        output = model(data)
                        return output

                    # Suggested fix:
                    # Apply deterministic settings only to relevant sections
                    # with torch.use_deterministic_algorithms(True):
                    #     output = model(data)
                    """
                ),
                "definition": (
                    "This smell refers to the unnecessary use "
                    "or failure to remove the setting "
                    "'torch.use_deterministic_algorithms(True)', "
                    "particularly when it is no longer needed in the pipeline."
                ),
                "rationale": (
                    "While deterministic algorithms are essential "
                    "for reproducibility in debugging and validation, they "
                    "can introduce significant performance overhead  "
                    "and restrict certain operations (e.g., non-deterministic "
                    "optimizations) in production. Properly "
                    "managing this setting ensures that "
                    "reproducibility is maintained when needed without "
                    "unnecessarily impacting performance or flexibility."
                ),
            },
            "In-Place APIs Misused": {
                "description": (
                    "This smell occurs when developers incorrectly "
                    "assume that changes to a Pandas DataFrame "
                    "are made in-place, or when they fail to capture "
                    "the result of an operation that does not modify "
                    "the DataFrame in-place by default. "
                    "This misunderstanding can lead to unintended "
                    "behavior, data loss, or increased debugging complexity."
                ),
                "example": (
                    """
                    import pandas as pd

                    # Create a sample DataFrame
                    data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
                    df = pd.DataFrame(data)

                    # Example 1: Dropping a column without capturing the result
                    df.drop('A')
                    # Code smell: Result of the drop operation is ignored

                    # Suggested fix:
                    # Capture the result of the operation
                    # df = df.drop('A')

                    # Example 2: Sorting values without capturing the result
                    df.sort_values('B')
                    # Code smell: Sorting is not
                    # applied to the original DataFrame

                    # Suggested fix:
                    # Assign the result back to the DataFrame
                    # df = df.sort_values('B')

                    # Example 3: Applying a function with
                    # `apply()` and ignoring the result
                    def square(x):
                        return x**2

                    df['B'].apply(square)  # Code smell: Result is ignored

                    # Suggested fix:
                    # Assign the result to a column or variable
                    # df['B'] = df['B'].apply(square)

                    # Example 4: Resetting the index without
                    # inplace=True or assignment
                    df.reset_index()  # Code smell: Ignoring the result

                    # Suggested fix:
                    # Use inplace=True or assign the result to the DataFrame
                    # df = df.reset_index()

                    # Example 5: Filling missing values with
                    # `fillna()` and ignoring the result
                    df['B'].fillna(0)  # Code smell: Result is ignored

                    # Suggested fix:
                    # Assign the result back to the DataFrame
                    # or use inplace=True
                    # df['B'] = df['B'].fillna(0)
                    # OR
                    # df['B'].fillna(0, inplace=True)
                    """
                ),
                "definition": (
                    "This smell refers to the incorrect use of Pandas "
                    "APIs where changes are assumed to be in-place "
                    "without explicitly assigning the result to a "
                    "variable or using the `inplace=True` parameter."
                ),
                "rationale": (
                    "Explicitly managing the results of Pandas API calls "
                    "ensures clarity, prevents unintended data loss, "
                    "and avoids subtle bugs caused by misunderstandings "
                    "about in-place versus non-in-place operations. "
                    "Using in-place operations sparingly or assigning the "
                    "results explicitly helps maintain predictable behavior."
                ),
            },
            "Empty Column Misinitialization": {
                "description": (
                    "This smell occurs when new columns in a Pandas DataFrame "
                    "are initialized with empty strings or zeros, "
                    "instead of using contextually appropriate default "
                    "values. This issue applies specifically to "
                    "columns in Pandas DataFrames "
                    "and does not concern other variables or data structures."
                ),
                "example": (
                    """
                    import pandas as pd

                    # Create a sample DataFrame
                    data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
                    df = pd.DataFrame(data)

                    # Example 1: Using empty strings for initialization
                    # Code smell: Initializing a new column with empty strings
                    df["new_column"] = ""
                    # Avoid using empty strings for column initialization

                    # Suggested fix:
                    # Use NaN for missing values to
                    # indicate uninitialized or null data
                    # df["new_column"] = pd.NA

                    # Example 2: Using zeros for numeric columns
                    # Code smell: Initializing a new
                    # numeric column with zeros without clear intent
                    df["numeric_column"] = 0
                    # Avoid defaulting to zero unless contextually appropriate

                    # Suggested fix:
                    # Use NaN to indicate missing numeric data
                    # df["numeric_column"] = pd.NA

                    # Example 3: Adding multiple columns with default values
                    # Code smell: Adding multiple
                    #  columns with the same default value
                    #  (e.g., empty strings)
                    df["col1"], df["col2"] = "", ""
                    # Avoid bulk initialization with empty strings

                    # Suggested fix:
                    # Use more meaningful defaults
                    #  or NaN based on column purpose
                    # df["col1"] = "default_value1"
                    # df["col2"] = "default_value2"

                    # Example 4: Dynamic column creation during iteration
                    for col_name in ["col3", "col4"]:
                        # Code smell: Using a loop to
                        #  initialize columns with zeros
                        df[col_name] = 0

                    # Suggested fix:
                    # Assign appropriate default values or use NaN
                    # for col_name in ["col3", "col4"]:
                    #     df[col_name] = pd.NA
                    """
                ),
                "definition": (
                    "This smell refers to the initialization of "
                    "new columns in a Pandas DataFrame "
                    "with default values such as "
                    "empty strings or zeros, instead of "
                    "using NaN or other contextually "
                    "meaningful default values."
                ),
                "rationale": (
                    "Using empty strings or zeros for initializing "
                    "DataFrame columns can lead to data "
                    "inconsistencies, misinterpretations, "
                    "and unintended behavior in downstream data "
                    "processing. Proper initialization ensures "
                    "data integrity, clarity, and facilitates accurate "
                    "analysis and transformations. Adopting NaN for "
                    "missing values or using "
                    "context-appropriate defaults improves "
                    "the overall quality of data management."
                ),
            },
            "Gradients Not Cleared Before Backward Propagation": {
                "description": (
                    "This smell occurs when gradients are not "
                    "cleared before performing backward propagation "
                    "in PyTorch. This can result in gradient "
                    "accumulation across iterations, leading to "
                    "incorrect updates, unintended behavior, "
                    "and potentially unstable training dynamics."
                ),
                "example": (
                    """
                    import torch
                    import torch.optim as optim

                    # Create model and optimizer
                    model = torch.nn.Linear(10, 2)
                    optimizer = optim.SGD(model.parameters(), lr=0.01)

                    # Example 1: Gradients not cleared in a single step
                    def single_step_training():
                        # Code smell: Gradients are not
                        #  cleared before backward propagation
                        loss = model(torch.randn(5, 10)).mean()
                        loss.backward()
                        optimizer.step()  # optimizer.zero_grad() is missing

                    # Suggested fix:
                    # Clear gradients explicitly before backward propagation
                    # optimizer.zero_grad()
                    # loss = model(torch.randn(5, 10)).mean()
                    # loss.backward()
                    # optimizer.step()

                    # Example 2: Gradient accumulation across iterations
                    def training_loop_with_accumulation(dataloader):
                        for inputs, targets in dataloader:
                            outputs = model(inputs)
                            loss = torch.nn.functional.mse_loss(
                                outputs, targets
                            )

                            # Code smell: Gradients from
                            #  previous steps are not cleared
                            loss.backward()
                            optimizer.step()

                    # Suggested fix:
                    # Use optimizer.zero_grad() at the beginning
                    #  of each iteration
                    # for inputs, targets in dataloader:
                    #     optimizer.zero_grad()
                    #     outputs = model(inputs)
                    #     loss = torch.nn.functional.mse_loss(outputs, targets)
                    #     loss.backward()
                    #     optimizer.step()

                    # Example 3: Mixed-precision training
                    #  without clearing gradients
                    scaler = torch.cuda.amp.GradScaler()

                    def mixed_precision_training_step():
                        with torch.cuda.amp.autocast():
                            loss = model(torch.randn(5, 10)).mean()

                        # Code smell: Forgetting to clear gradients
                        #  in mixed-precision training
                        scaler.scale(loss).backward()
                        scaler.step(optimizer)
                        scaler.update()
                    """
                ),
                "definition": (
                    "This smell refers to the omission of "
                    "optimizer.zero_grad() before performing "
                    "loss_fn.backward() in PyTorch, causing "
                    "gradients from previous steps to accumulate "
                    "and potentially destabilizing the training process."
                ),
                "rationale": (
                    "In PyTorch, gradients are accumulated by "
                    "default. If optimizer.zero_grad() is not used, "
                    "the gradients from previous steps are "
                    "added to the current gradients, leading "
                    "to incorrect parameter updates. "
                    "Clearing gradients before backward "
                    "propagation ensures accurate updates, "
                    "prevents gradient accumulation, "
                    "and maintains stable training behavior."
                ),
            },
            "Memory Not Freed": {
                "description": (
                    "This smell refers to the declaration of "
                    "machine learning models or large objects within loops, "
                    "without explicitly releasing memory after "
                    "each iteration. This practice can lead to memory leaks, "
                    "inefficient resource utilization, and "
                    "potential crashes in resource-constrained environments, "
                    "particularly when working with GPU memory."
                ),
                "example": (
                    """
                    import torch

                    # Example 1: Declaring a model inside a
                    #  loop without releasing memory
                    def process_data(dataset):
                        for data in dataset:
                            # Code smell: Model is created in each
                            #  iteration but memory is not freed
                            model = torch.nn.Linear(10, 2)
                            output = model(data)

                    # Suggested fix:
                    # Release memory explicitly after using the model
                    # for data in dataset:
                    #     model = torch.nn.Linear(10, 2)
                    #     output = model(data)
                    #     del model  # Free memory
                    #     torch.cuda.empty_cache()  # If using GPU

                    # Example 2: Tensor creation inside loops
                    #  without clearing memory
                    def process_tensors(tensor_list):
                        for tensor in tensor_list:
                            # Code smell: Temporary tensors created in
                            #  loop are not cleared
                            temp_tensor = tensor + torch.randn(tensor.size())

                    # Suggested fix:
                    # Use del and clear caches for temporary tensors
                    # for tensor in tensor_list:
                    #     temp_tensor = tensor + torch.randn(tensor.size())
                    #     del temp_tensor
                    #     torch.cuda.empty_cache()

                    # Example 3: Model training loop with memory leaks
                    def train_multiple_models(data, num_models):
                        for _ in range(num_models):
                            # Code smell: Memory for models and
                            #  optimizers is not released
                            model = torch.nn.Linear(10, 2)
                            optimizer = torch.optim.SGD(
                                model.parameters(), lr=0.01
                            )
                            output = model(data)
                            loss = output.sum()
                            loss.backward()
                            optimizer.step()

                    # Suggested fix:
                    # Free memory for models and optimizers explicitly
                    # for _ in range(num_models):
                    #     model = torch.nn.Linear(10, 2)
                    #     optimizer = torch.optim.SGD(
                    #           model.parameters(), lr=0.01
                    #     )
                    #     output = model(data)
                    #     loss = output.sum()
                    #     loss.backward()
                    #     optimizer.step()
                    #     del model, optimizer  # Release memory
                    #     torch.cuda.empty_cache()  # If using GPU
                    """
                ),
                "definition": (
                    "This smell occurs when machine learning models, "
                    "tensors, or other memory-intensive objects "
                    "are declared inside loops without explicitly "
                    "freeing the memory after each iteration."
                ),
                "rationale": (
                    "Memory leaks caused by failing to release memory "
                    "in loops can significantly impact the performance "
                    "and reliability of machine learning workflows, "
                    "especially in GPU-accelerated environments. "
                    "Explicit memory management practices, such as "
                    "using `del` and `torch.cuda.empty_cache()`, "
                    "help avoid crashes, reduce memory fragmentation, "
                    "and ensure optimal resource usage."
                ),
            },
            "Merge API Parameter Not Explicitly Set": {
                "description": (
                    "This smell occurs when the 'how' and 'on' "
                    "parameters are not explicitly defined during a Pandas "
                    "merge operation. This can lead to potential "
                    "ambiguity, unexpected behavior, or incorrect results, "
                    "as the default settings may not align with the "
                    "developer's intent. Explicitly specifying these "
                    "parameters ensures clarity and better "
                    "maintainability of the code."
                ),
                "example": (
                    """
                    import pandas as pd

                    # Create sample DataFrames
                    df1 = pd.DataFrame(
                        {'key': [1, 2, 3], 'value1': ['A', 'B', 'C']}
                    )
                    df2 = pd.DataFrame(
                        {'key': [2, 3, 4], 'value2': ['X', 'Y', 'Z']}
                    )

                    # Example 1: Ambiguous merge
                    # without specifying 'how' and 'on'
                    df_merged = df1.merge(df2)
                    # Code smell: Default 'how' is
                    #  'inner', and 'on' is inferred

                    # Suggested fix:
                    # Explicitly specify 'how' and 'on' parameters
                    # df_merged = df1.merge(df2, how='inner', on='key')

                    # Example 2: Outer join without specifying 'on' explicitly
                    df_merged = df1.merge(df2, how='outer')
                    # Code smell: 'on' parameter is inferred

                    # Suggested fix:
                    # Explicitly specify 'on' parameter
                    # df_merged = df1.merge(df2, how='outer', on='key')

                    # Example 3: Merge operation
                    # without clarity on key alignment
                    df3 = pd.DataFrame(
                        {'id': [1, 2, 3], 'value3': ['P', 'Q', 'R']}
                    )
                    df_merged = df1.merge(df3)
                    # Code smell: 'on' is inferred but may
                    # not align with intent

                    # Suggested fix:
                    # Use 'left_on' and 'right_on' for clarity
                    # df_merged = df1.merge(
                    #   df3, how='inner', left_on='key', right_on='id'
                    # )

                    # Example 4: Merging on
                    # indices without explicit specification
                    df1.set_index('key', inplace=True)
                    df2.set_index('key', inplace=True)
                    df_merged = df1.merge(df2)
                    # Code smell: Index-based merge not explicitly stated

                    # Suggested fix:
                    # Explicitly set 'left_index' and 'right_index'
                    # df_merged = df1.merge(
                    #   df2, how='inner', left_index=True, right_index=True
                    # )
                    """
                ),
                "definition": (
                    "This smell refers to the omission of "
                    "explicit specification of the 'how' and 'on' parameters "
                    "in Pandas merge operations. This can "
                    "result in unclear behavior and "
                    "potential misalignment with "
                    "the intended data manipulation."
                ),
                "rationale": (
                    "Specifying the 'how' and 'on' parameters "
                    "in merge operations is essential for "
                    "ensuring clarity and "
                    "avoiding errors in data alignment. "
                    "Default settings for these parameters "
                    "may lead to ambiguity, "
                    "making the code harder to understand and "
                    "maintain. Explicit definitions make the merge operation "
                    "more predictable and align it with the "
                    "developer's intentions."
                ),
            },
            "NaN Equivalence Comparison Misused": {
                "description": (
                    "This smell occurs when 'np.nan' is used in "
                    "equivalence comparisons to check for NaN values "
                    "specifically within columns of a Pandas "
                    "DataFrame. Such comparisons are invalid "
                    "because NaN values are not equal to themselves, "
                    "leading to incorrect logic. Proper "
                    "handling requires using methods like "
                    "pd.isna() or pd.isnull(), which are "
                    "designed for NaN detection in DataFrames."
                ),
                "example": (
                    """
                    import numpy as np
                    import pandas as pd

                    # Create a sample DataFrame
                    df = pd.DataFrame({'column': [1, 2, np.nan, 4]})

                    # Example 1: Incorrect equivalence comparison
                    def check_values_incorrect(df):
                        # Code smell: Using 'np.nan' for
                        # equivalence comparison in a DataFrame column
                        for value in df['column']:
                            if value == np.nan:
                                # This will always evaluate to False
                                print("Value is NaN")

                    # Suggested fix:
                    # Use pd.isna() for proper NaN checking
                    # def check_values_correct(df):
                    #     for value in df['column']:
                    #         if pd.isna(value):
                    #             print("Value is NaN")

                    # Example 2: Filtering rows with NaN values
                    # Code smell: Incorrect filtering using 'np.nan'
                    filtered_df = df[df['column'] != np.nan]
                     # This will not filter NaN rows

                    # Suggested fix:
                    # Use pd.notna() to filter out NaN values
                    # filtered_df = df[pd.notna(df['column'])]

                    # Example 3: Conditional replacement of NaN values
                    # Code smell: Conditional
                    # replacement using 'np.nan' equivalence
                    df['column'] = [
                    0 if value == np.nan else value for value in df['column']
                    ]

                    # Suggested fix:
                    # Use pd.isna() for conditional replacement
                    # df['column'] = [
                    # 0 if pd.isna(value) else value for value in df['column']
                    # ]
                    """
                ),
                "definition": (
                    "This smell refers to the misuse of 'np.nan' "
                    "in equivalence comparisons with values from "
                    "columns in a Pandas DataFrame. Such "
                    "comparisons always evaluate to False due to the unique "
                    "properties of NaN values."
                ),
                "rationale": (
                    "NaN values are not equal to themselves, "
                    "making equivalence comparisons with 'np.nan' inherently "
                    "invalid. This can lead to logical errors "
                    "when working with Pandas DataFrames, where NaN handling "
                    "is a common requirement. Using methods like "
                    "pd.isna() or pd.notna() ensures accurate identification "
                    "and handling of NaN values, leading to "
                    "correct and predictable behavior in data "
                    "processing pipelines."
                ),
            },
            "TensorArray Not Used": {
                "description": (
                    "This smell occurs when 'tf.constant()' "
                    "is used to initialize tensors inside a "
                    "loop in TensorFlow, instead of utilizing "
                    "'tf.TensorArray()', which is specifically "
                    "designed for efficient tensor handling "
                    "in iterative operations. This issue is "
                    "specific to TensorFlow operations and "
                    "does not apply to tensor-related "
                    "operations in other frameworks such as "
                    "PyTorch or loops that do not involve TensorFlow."
                ),
                "example": (
                    """
                    import tensorflow as tf

                    # Example 1: Using tf.constant() in a loop
                    def process_tensors(n):
                        # Code smell: Inefficient
                        # tensor initialization in a TensorFlow loop
                        for i in range(n):
                            tensor = tf.constant([1, 2, 3])
                            # Creates a new tensor in each iteration

                    # Suggested fix:
                    # Use tf.TensorArray() to efficiently
                    # handle tensor initialization in loops
                    # def process_tensors_fixed(n):
                    #     tensor_array = tf.TensorArray(dtype=tf.int32, size=n)
                    #     for i in range(n):
                    #         tensor_array = tensor_array.write(i, [1, 2, 3])

                    # Example 2: Dynamic tensor
                    # creation inside a loop without TensorArray
                    def compute_gradients(n):
                        for i in range(n):
                            # Code smell: Repeatedly
                            #  creating tensors with tf.constant()
                            gradient = tf.constant([0.1, 0.2, 0.3]) * i

                    # Suggested fix:
                    # Use TensorArray to store and manage gradients
                    # def compute_gradients_fixed(n):
                    #     gradient_array = tf.TensorArray(
                    #           dtype=tf.float32, size=n
                    #     )
                    #     for i in range(n):
                    #         gradient = [0.1, 0.2, 0.3] * i
                    #         gradient_array = gradient_array.write(
                    #           i, gradient
                    #           )

                    # Example 3: Storing results of iterative tensor operations
                    def iterative_operations(n):
                        results = []
                        for i in range(n):
                            # Code smell: Appending tensors
                            # to a Python list instead of using TensorArray
                            result = tf.constant([i, i+1, i+2])
                            results.append(result)

                    # Suggested fix:
                    # Replace the Python list with a TensorArray
                    # def iterative_operations_fixed(n):
                    #     results_array = tf.TensorArray(
                    #       dtype=tf.int32, size=n
                    #     )
                    #     for i in range(n):
                    #         result = [i, i+1, i+2]
                    #         results_array = results_array.write(i, result)
                    """
                ),
                "definition": (
                    "This smell refers to the use of "
                    "'tf.constant()' inside a loop in "
                    "TensorFlow to repeatedly create tensors, "
                    "instead of leveraging 'tf.TensorArray()' "
                    "for efficient and scalable tensor "
                    "handling during iterative operations."
                ),
                "rationale": (
                    "Repeated creation of tensors with 'tf.constant()' "
                    "inside loops can lead to memory inefficiency "
                    "and runtime errors, "
                    "especially in scenarios involving a "
                    "large number of iterations. "
                    "'tf.TensorArray()' is explicitly designed to "
                    "optimize tensor operations in loops "
                    "by reducing memory overhead and "
                    "improving performance. Proper use of "
                    "'tf.TensorArray()' ensures that "
                    "iterative tensor manipulations are "
                    "efficient and maintainable."
                ),
            },
            "Hyperparameter Not Explicitly Set": {
                "description": (
                    "This smell occurs when a developer does not "
                    "explicitly set the hyperparameters of a machine "
                    "learning algorithm. "
                    "This oversight can lead to non-reproducible "
                    "results, suboptimal model performance, and "
                    "a lack of clarity in the model's configuration. "
                    "The issue is prevalent across a wide range "
                    "of models, including:\n"
                    "- **Decision Trees**: DecisionTreeClassifier "
                    "and DecisionTreeRegressor (e.g., "
                    "max_depth, min_samples_split)\n"
                    "- **Random Forests**: RandomForestClassifier "
                    "and RandomForestRegressor (e.g., n_estimators, "
                    "max_depth, random_state)\n"
                    "- **Gradient Boosting Methods**: "
                    "GradientBoostingClassifier and "
                    "GradientBoostingRegressor (e.g., "
                    "learning_rate, n_estimators, max_depth)\n"
                    "- **Boosting Frameworks**: XGBoost and "
                    "LightGBM (e.g., learning_rate, num_leaves, max_depth)\n"
                    "- **Linear Models**: LogisticRegression "
                    "(e.g., C, solver, max_iter)\n"
                    "- **Support Vector Machines**: SVC and SVR "
                    "(e.g., C, kernel, gamma)\n"
                    "- **Nearest Neighbors**: KNeighborsClassifier "
                    "and KNeighborsRegressor (e.g., n_neighbors, "
                    "weights, metric)\n"
                    "- **Neural Networks**: Configurations such "
                    "as number of layers, learning rate, and "
                    "activation functions\n"
                    "- **Clustering Algorithms**: KMeans "
                    "(e.g., n_clusters, init)\n"
                    "- **Dimensionality Reduction**: PCA "
                    "(e.g., n_components)\n"
                    "- **Ensemble Methods**: AdaBoostClassifier "
                    "(e.g., n_estimators, learning_rate)."
                ),
                "example": (
                    """
                    # Example with scikit-learn (generalized for any model)
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.svm import SVC

                    def train_random_forest(X, y):
                        # Code smell: Hyperparameters are not explicitly set
                        model = RandomForestClassifier()
                        # Default values for hyperparameters are used
                        model.fit(X, y)

                    def train_svm(X, y):
                        # Code smell: Hyperparameters are not explicitly set
                        model = SVC()
                        # Default kernel and hyperparameters are used
                        model.fit(X, y)

                    # Suggested fix for RandomForestClassifier:
                    # Explicitly set hyperparameters
                    #  for reproducibility and clarity
                    # model = RandomForestClassifier(
                    #     n_estimators=100, max_depth=10, random_state=42
                    # )
                    # model.fit(X, y)

                    # Suggested fix for SVC:
                    # Explicitly set kernel
                    #  and hyperparameters for reproducibility
                    # model = SVC(kernel='rbf', C=1.0, gamma='scale')
                    # model.fit(X, y)
                    """
                ),
                "definition": (
                    "This smell refers to the failure to "
                    "explicitly set hyperparameters when "
                    "configuring machine learning models. "
                    "Default hyperparameters may not suit the "
                    "specific dataset or problem and can lead "
                    "to reduced performance or reproducibility issues."
                ),
                "rationale": (
                    "Explicit hyperparameter tuning is a critical "
                    "step in building robust machine learning models. "
                    "Default settings are often generic and may "
                    "not optimize the model's performance for a "
                    "given dataset. Furthermore, explicitly "
                    "specifying hyperparameters ensures reproducibility, "
                    "facilitates better communication of the "
                    "model's design, and avoids unintended "
                    "consequences in production. This applies particularly "
                    "to widely used models such as decision trees, "
                    "random forests, gradient boosting frameworks, "
                    "support vector machines, and clustering algorithms."
                ),
            },
            "Matrix Multiplication API Misused": {
                "description": (
                    "This smell refers to the use of 'np.dot' "
                    "for matrix multiplication in NumPy, "
                    "which has been superseded by modern "
                    "alternatives like the '@' operator or 'np.matmul'. "
                    "These newer methods offer improved "
                    "readability, are more intuitive for developers, "
                    "and align better with current coding "
                    "standards. The '@' operator, introduced in Python 3.5, "
                    "is particularly preferred for its simplicity "
                    "and explicitness in representing matrix multiplication."
                ),
                "example": (
                    """
                    import numpy as np

                    # Example 1: Basic matrix multiplication
                    def multiply_matrices(matrix_a, matrix_b):
                        # Code smell: Using np.dot for matrix multiplication
                        result = np.dot(matrix_a, matrix_b)
                        # Avoid using np.dot for matrices

                        # Suggested fix:
                        # Use the '@' operator for better
                        #  readability and modern standards
                        # result = matrix_a @ matrix_b

                        # Alternatively, use np.matmul
                        #  for explicit function calls
                        # result = np.matmul(matrix_a, matrix_b)

                        return result

                    # Example 2: Misusing np.dot for vector dot product
                    def dot_product(vector_a, vector_b):
                        # Code smell: Using np.dot for vectors
                        #  (potentially confusing)
                        result = np.dot(vector_a, vector_b)
                            # Allowed but less clear

                        # Suggested fix:
                        # Use '@' operator to make operations consistent
                        # result = vector_a @ vector_b

                        return result

                    # Example 3: Multiplying higher-dimensional arrays
                    def multiply_higher_dim_arrays(array_a, array_b):
                        # Code smell: Using np.dot
                        #  for higher-dimensional arrays
                        result = np.dot(array_a, array_b)

                        # Suggested fix:
                        # Use np.matmul for clarity when working
                        #  with higher-dimensional arrays
                        # result = np.matmul(array_a, array_b)

                        return result
                    """
                ),
                "definition": (
                    "This smell occurs when 'np.dot' is used for "
                    "matrix multiplication in NumPy, "
                    "rather than modern alternatives like the "
                    "'@' operator or 'np.matmul', which "
                    "are more readable and better suited "
                    "for this operation."
                ),
                "rationale": (
                    "Using 'np.dot' for matrix multiplication can "
                    "lead to confusion because it also "
                    "supports dot products for vectors. "
                    "Modern alternatives like the '@' operator and "
                    "'np.matmul' explicitly differentiate "
                    "matrix multiplication, improving readability "
                    "and reducing potential ambiguity. "
                    "Adopting these methods ensures code consistency "
                    "and aligns with contemporary Python and NumPy standards."
                ),
            },
            "PyTorch Call Method Misused": {
                "description": (
                    "This smell occurs specifically when a "
                    "developer explicitly calls 'self.net.forward()' "
                    "to forward input through a PyTorch network, "
                    "instead of using the model instance as a callable "
                    "(e.g., 'self.net(input)'). This misuse bypasses "
                    "important internal mechanisms in PyTorch, "
                    "such as hooks, pre-processing, and "
                    "post-processing operations tied to the forward pass. "
                    "Using the model instance directly ensures "
                    "consistency with PyTorch's design "
                    "principles and best practices."
                ),
                "example": (
                    """
                    import torch
                    import torch.nn as nn

                    # Example 1: Basic misuse in a single module
                    class MyModel(nn.Module):
                        def __init__(self):
                            super(MyModel, self).__init__()
                            self.net = nn.Linear(10, 5)

                        def forward(self, x):
                            # Code smell: Explicitly calling self.net.forward()
                            output = self.net.forward(x)
                                # Should use self.net(x) instead
                            return output

                    # Example 2: Misuse in a multi-layer model
                    class MultiLayerModel(nn.Module):
                        def __init__(self):
                            super(MultiLayerModel, self).__init__()
                            self.layer1 = nn.Linear(10, 20)
                            self.layer2 = nn.Linear(20, 5)

                        def forward(self, x):
                            # Code smell: Using forward()
                            #  explicitly for both layers
                            x = self.layer1.forward(x)
                              # Should use self.layer1(x) instead
                            output = self.layer2.forward(x)
                              # Should use self.layer2(x) instead
                            return output

                    # Example 3: Misuse in a sequential model
                    class SequentialModel(nn.Module):
                        def __init__(self):
                            super(SequentialModel, self).__init__()
                            self.model = nn.Sequential(
                                nn.Linear(10, 20),
                                nn.ReLU(),
                                nn.Linear(20, 5)
                            )

                        def forward(self, x):
                            # Code smell: Explicitly
                            #  calling forward() on a Sequential model
                            output = self.model.forward(x)
                                # Should use self.model(x) instead
                            return output

                    # Suggested fixes:
                    # In all cases above, replace
                    #  self.net.forward(x) with self.net(x).
                    # Example fix for MyModel:
                    # class MyModelFixed(nn.Module):
                    #     def __init__(self):
                    #         super(MyModelFixed, self).__init__()
                    #         self.net = nn.Linear(10, 5)

                    #     def forward(self, x):
                    #         # Use the model instance as a callable
                    #         output = self.net(x)
                    #         return output
                    """
                ),
                "definition": (
                    "This smell refers to explicitly calling "
                    "the 'forward' method of a PyTorch module "
                    "instance (e.g., 'self.net.forward()') "
                    "instead of using the instance itself as a callable "
                    "(e.g., 'self.net(input)') during the forward pass."
                ),
                "rationale": (
                    "Using the model instance as a callable (e.g., "
                    "'self.net(input)') ensures compatibility "
                    "with PyTorch's internal mechanisms, such "
                    "as hooks for debugging, gradient computation, "
                    "and distributed training operations. Explicitly "
                    "calling 'self.net.forward()' bypasses these features, "
                    "potentially leading to incorrect behavior, "
                    "incomplete gradient computation, or incompatibility with "
                    "framework-level features like model checkpointing "
                    "or profiling. This smell is specific to PyTorch's "
                    "'forward' method and should not be mistakenly "
                    "applied to unrelated methods or contexts."
                ),
            },
            "Unnecessary Iteration": {
                "description": (
                    "This smell occurs when a developer uses "
                    "an explicit loop to perform "
                    "row-wise or element-wise operations directly "
                    "on the data of a Pandas DataFrame. "
                    "Instead of leveraging Pandas' efficient "
                    "vectorized operations, the use of loops "
                    "in this specific context leads to slower "
                    "execution, higher memory usage, and "
                    "increased code complexity. This smell "
                    "applies exclusively to operations involving "
                    "Pandas DataFrame objects and does not "
                    "include other loops or iterations unrelated "
                    "to DataFrame processing."
                ),
                "example": (
                    """
                    import pandas as pd

                    # Create a sample DataFrame
                    df = pd.DataFrame({'existing_col': [1, 2, 3]})

                    # Code smell: Using a loop to create
                    #  a new column in the DataFrame
                    for index, row in df.iterrows():
                        df.loc[index, 'new_col'] = row['existing_col'] * 2
                            # Inefficient

                    # Suggested fix:
                    # Replace the loop with a vectorized operation
                    # df['new_col'] = df['existing_col'] * 2

                    # Example 2: Using apply incorrectly for simple operations
                    df['new_col'] = df['existing_col'].apply(lambda x: x * 2)
                        # Avoid if a direct vectorized operation is possible

                    # Suggested fix:
                    # df['new_col'] = df['existing_col'] * 2

                    # Example 3: Nested loop for conditional column updates
                    for index, row in df.iterrows():
                        if row['existing_col'] > 1:
                            df.loc[index, 'flag'] = 1
                        else:
                            df.loc[index, 'flag'] = 0  # Inefficient

                    # Suggested fix:
                    # df['flag'] = (df['existing_col'] > 1).astype(int)
                    """
                ),
                "definition": (
                    "This smell refers to the use of explicit "
                    "loops (e.g., for loops, iterrows) "
                    "to perform operations on Pandas DataFrame "
                    "objects, instead of using Pandas' "
                    "vectorized methods. It does not apply to "
                    "general-purpose loops or iterations "
                    "unrelated to DataFrames."
                ),
                "rationale": (
                    "Performing operations on Pandas DataFrame data "
                    "using loops is inefficient because "
                    "it processes rows or elements one at a time. "
                    "Pandas' vectorized operations are optimized "
                    "for these tasks, significantly improving "
                    "performance, reducing code complexity, and "
                    "lowering the risk of errors. This smell is "
                    "specific to DataFrame operations, ensuring that "
                    "other forms of iteration are not mistakenly "
                    "flagged as unnecessary."
                ),
            },
        }

    def inject_smells(self, clean_function, num_smells=None):
        """
        Injects code smells into a clean Python function.

        Args:
            clean_function (str): The source code of the "
            "clean function as a string.
            num_smells (int, optional): Maximum number of "
            "code smells to inject. Defaults to `self.max_smells`.

        Returns:
            str: The source code of the function with injected code smells.
        """
        if num_smells is None:
            num_smells = self.max_smells

        # Select smells randomly, up to the maximum allowed
        selected_smells = self._select_smells(random.randint(1, num_smells))

        # Build the prompt dynamically
        prompt = self._build_prompt(clean_function, selected_smells)

        # Call the LLM to generate the smelly function
        response = self.llm_model.generate_response(prompt)

        if response.startswith("```python") and response.endswith("```"):
            response = response[9:-3].strip()

        return response, selected_smells

    def _select_smells(self, num_smells):
        """
        Selects a set of code smells based on equal distribution.

        Args:
            num_smells (int): Number of code smells to select.

        Returns:
            list: A list of selected code smell names.
        """
        smells = list(self.smell_descriptions.keys())

        # Randomly select smells with equal probability
        return random.sample(smells, k=num_smells)

    def _build_prompt(self, clean_function, selected_smells):
        """
        Builds the prompt to instruct the LLM to inject code smells.

        Args:
            clean_function (str): The source code of the clean function.
            selected_smells (list): The selected code smells to inject.

        Returns:
            str: The prompt to send to the LLM.
        """
        # Construct details of the smells to inject
        smells_details = "\n\n".join(
            [
                f"- {smell}:\n"
                f"  Description: "
                f"{self.smell_descriptions[smell]['description']}\n"
                f"  Example: "
                f"{self.smell_descriptions[smell]['example']}\n"
                f"  Definition: "
                f"{self.smell_descriptions[smell]['definition']}\n"
                f"  Rationale: {self.smell_descriptions[smell]['rationale']}"
                for smell in selected_smells
            ]
        )

        prompt = (
            "You are a code generation assistant specializing in introducing "
            'intentional flaws ("code smells") into Python code. '
            "Below is a clean Python method:\n\n"
            f"{clean_function}\n\n"
            "Task:\n"
            "1. Modify the function above to introduce the "
            "following code smells:\n"
            f"{smells_details}\n\n"
            "2. Ensure the function remains functional but "
            "reflects the specified flaws.\n"
            "3. Do not create any new methods or functions. "
            "All modifications must be "
            "made within the given function.\n"
            "4. Do not add any imports or modify the import statements.\n"
            "5. Return only the modified function code.\n"
            "Instructions:\n"
            "- Inject the specified code smells directly into the function.\n"
            "- Take precise inspiration from the provided examples "
            "of code smells to ensure their characteristics "
            "are accurately reflected. "
            "If integrating a code smell into the given "
            "function is not possible, "
            "append a new snippet (even if out of context) "
            "showcasing the code smell, "
            "ensuring it aligns closely with the examples provided.\n"
            "- Do not include any additional comments, explanations, "
            "or external dependencies.\n"
        )

        return prompt
