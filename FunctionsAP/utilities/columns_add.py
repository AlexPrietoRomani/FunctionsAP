import pandas as pd
import numpy as np

def columns_add(dataframe, columns, name_column_new=None, type="Number", drop=True, separator="", operation=None):
    """
    Combina o agrega columnas del DataFrame, ya sean de tipo numérico, texto o fecha.

    Parámetros:
        - dataframe (pd.DataFrame): DataFrame sobre el cual se realizará la operación.
        - columns (list): Lista de nombres de columnas que se desea combinar o agregar.
        - name_column_new (str, opcional): Nombre de la nueva columna a crear. Si es None, se usa el nombre de la primera columna en 'columns'.
        - type (str): Tipo de datos de las columnas a combinar o agregar. Opciones: "Number", "Text", "Date".
        - drop (bool): Indica si las columnas originales deben ser eliminadas después de la operación. Por defecto es True.
        - separator (str): Separador utilizado al concatenar columnas de texto. Solo aplica si type="Text".
        - operation (str, opcional): Operación a realizar.
            - Para "Number": "sum"(defecto), "mean", "prod", "min", "max", "first".
            - Para "Text": "concat"(defecto), "first".
            - Para "Date": "min", "max", "mean"(defecto), "first".

    Retorna:
        - pd.DataFrame: DataFrame con la nueva columna agregada. Si 'drop' es True, las columnas originales son eliminadas.
    """

    # Validaciones iniciales
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("El argumento 'dataframe' debe ser un pandas DataFrame.")

    if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
        raise TypeError("El argumento 'columns' debe ser una lista de nombres de columnas (str).")

    if not set(columns).issubset(dataframe.columns):
        missing_columns = list(set(columns) - set(dataframe.columns))
        raise ValueError(f"Las siguientes columnas no se encontraron en el DataFrame: {missing_columns}")

    if name_column_new is None:
        name_column_new = columns[0]

    if type.lower() not in ["number", "text", "date"]:
        raise ValueError("El argumento 'type' debe ser 'Number', 'Text' o 'Date'.")

    # Establecer la operación predeterminada según el tipo si 'operation' es None
    if operation is None:
        if type.lower() == "number":
            operation = "sum"
        elif type.lower() == "text":
            operation = "concat"
        elif type.lower() == "date":
            operation = "mean"
        else:
            raise ValueError(f"Tipo '{type}' no soportado.")

    # Copiar el DataFrame para no modificar el original
    df = dataframe.copy()

    # Definir un nombre temporal para evitar colisiones con columnas existentes
    temp_column_name = f"CoL$&$umNa_CreADA_{name_column_new}"
    while temp_column_name in df.columns:
        temp_column_name += "_temp"

    if type.lower() == "number":
        # Validar que las columnas sean numéricas
        if not all(pd.api.types.is_numeric_dtype(df[col]) for col in columns):
            raise TypeError("Todas las columnas deben ser numéricas para 'type'='Number'.")

        # Realizar la operación aritmética especificada
        if operation == "sum":
            df[temp_column_name] = df[columns].sum(axis=1, skipna=True)
        elif operation == "mean":
            df[temp_column_name] = df[columns].mean(axis=1, skipna=True)
        elif operation == "prod":
            df[temp_column_name] = df[columns].prod(axis=1, skipna=True)
        elif operation == "min":
            df[temp_column_name] = df[columns].min(axis=1, skipna=True)
        elif operation == "max":
            df[temp_column_name] = df[columns].max(axis=1, skipna=True)
        elif operation == "first":
            df[temp_column_name] = df[columns].bfill(axis=1).iloc[:, 0]
        else:
            raise ValueError(f"Operación '{operation}' no soportada para 'type'='Number'.")

    elif type.lower() == "text":
        # Concatenar columnas de texto con el separador especificado
        if operation == "concat":
            df[temp_column_name] = df[columns].astype(str).replace(['', 'nan', 'None'], np.nan).fillna('').agg(separator.join, axis=1)
        elif operation == "first":
            df[temp_column_name] = df[columns].astype(str).replace(['', 'nan', 'None'], np.nan).bfill(axis=1).iloc[:, 0]
        else:
            raise ValueError(f"Operación '{operation}' no soportada para 'type'='Text'.")

    elif type.lower() == "date":
        # Convertir columnas a datetime
        for col in columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        if operation == "min":
            df[temp_column_name] = df[columns].min(axis=1)
        elif operation == "max":
            df[temp_column_name] = df[columns].max(axis=1)
        elif operation == "mean":
            df[temp_column_name] = pd.to_datetime(df[columns].mean(axis=1), errors='coerce')
        elif operation == "first":
            df[temp_column_name] = df[columns].bfill(axis=1).iloc[:, 0]
        else:
            raise ValueError(f"Operación '{operation}' no soportada para 'type'='Date'.")

    else:
        raise ValueError(f"Tipo '{type}' no soportado.")

    # Eliminar columnas originales si drop es True
    if drop:
        df.drop(columns=columns, inplace=True)

    # Renombrar la columna temporal al nombre especificado
    df.rename(columns={temp_column_name: name_column_new}, inplace=True)

    return df