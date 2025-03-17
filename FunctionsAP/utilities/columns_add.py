import pandas as pd
import numpy as np

def columns_add(
    dataframe: pd.DataFrame,
    columns: list,
    name_column_new: str = None,
    type: str = "Number",
    drop: bool = True,
    separator: str = "",
    operation: str = None
) -> pd.DataFrame:
    """
    Combina o agrega columnas de un DataFrame, generando una nueva columna a partir de las especificadas.

    Parámetros:
        dataframe (pd.DataFrame): DataFrame sobre el cual se realizará la operación.
        columns (list): Lista de nombres de columnas que se desea combinar o agregar.
        name_column_new (str, opcional): Nombre de la nueva columna a crear. Si es None, se usará el nombre de la primera columna en 'columns'.
        type (str): Tipo de datos de las columnas a combinar o agregar. Opciones: "Number", "Text", "Date". (No distingue mayúsculas/minúsculas)
        drop (bool): Indica si las columnas originales deben ser eliminadas después de la operación. Por defecto es True.
        separator (str): Separador utilizado al concatenar columnas de texto (solo aplica si type="Text").
        operation (str, opcional): Operación a realizar:
            - Para "Number": "sum" (por defecto), "mean", "prod", "min", "max", "first".
            - Para "Text": "concat" (por defecto), "first".
            - Para "Date": "min", "max", "mean" (por defecto), "first".
    
    Retorna:
        pd.DataFrame: DataFrame con la nueva columna agregada. Si 'drop' es True, se eliminan las columnas originales.
    
    Ejemplo de uso:
        df_mod = columns_add(df, ["col1", "col2", "col3"], name_column_new="Sumatoria", type="Number", operation="sum")
    """
    # Validar que se haya pasado un DataFrame
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("El argumento 'dataframe' debe ser un pandas DataFrame.")
    
    # Validar que 'columns' es una lista de strings
    if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
        raise TypeError("El argumento 'columns' debe ser una lista de nombres de columnas (str).")
    
    # Verificar que todas las columnas estén en el DataFrame
    missing_columns = list(set(columns) - set(dataframe.columns))
    if missing_columns:
        raise ValueError(f"Las siguientes columnas no se encontraron en el DataFrame: {missing_columns}")
    
    # Si no se especifica el nombre para la nueva columna, se usa el nombre de la primera columna de la lista
    if name_column_new is None:
        name_column_new = columns[0]
    
    # Validar que el tipo es uno de los permitidos (sin distinguir mayúsculas/minúsculas)
    if type.lower() not in ["number", "text", "date"]:
        raise ValueError("El argumento 'type' debe ser 'Number', 'Text' o 'Date'.")
    
    # Si no se especifica la operación, se asigna una operación por defecto según el tipo
    if operation is None:
        if type.lower() == "number":
            operation = "sum"
        elif type.lower() == "text":
            operation = "concat"
        elif type.lower() == "date":
            operation = "mean"
        else:
            raise ValueError(f"Tipo '{type}' no soportado.")
    
    # Crear una copia del DataFrame para no modificar el original
    df = dataframe.copy()
    
    # Definir un nombre temporal para la nueva columna para evitar conflictos con nombres existentes
    temp_column_name = f"CoL$&$umNa_CreADA_{name_column_new}"
    while temp_column_name in df.columns:
        temp_column_name += "_temp"
    
    # Procesar según el tipo de datos
    if type.lower() == "number":
        # Validar que todas las columnas sean numéricas
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
            # Rellenar hacia adelante y tomar la primera columna no nula
            df[temp_column_name] = df[columns].bfill(axis=1).iloc[:, 0]
        else:
            raise ValueError(f"Operación '{operation}' no soportada para 'type'='Number'.")
    
    elif type.lower() == "text":
        # Convertir las columnas a string, reemplazar cadenas vacías o "nan" por NaN, y concatenar
        if operation == "concat":
            df[temp_column_name] = df[columns].apply(
                lambda row: separator.join(
                    [str(x) for x in row if str(x).lower() not in ['', 'nan', 'none']]
                ) if not all(str(x).lower() in ['', 'nan', 'none'] for x in row) else separator,
                axis=1
                ).replace(separator,np.nan)
        elif operation == "first":
            df[temp_column_name] = df[columns].astype(str)\
                .replace(['', 'nan', 'None'], np.nan)\
                .bfill(axis=1).iloc[:, 0]
        else:
            raise ValueError(f"Operación '{operation}' no soportada para 'type'='Text'.")
    
    elif type.lower() == "date":
        # Convertir las columnas especificadas a tipo datetime, con errores convertidos a NaT
        for col in columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Realizar la operación de fecha indicada
        if operation == "min":
            df[temp_column_name] = df[columns].min(axis=1)
        elif operation == "max":
            df[temp_column_name] = df[columns].max(axis=1)
        elif operation == "mean":
            # La media de fechas se calcula como la media de los valores numéricos subyacentes y luego se convierte a datetime
            df[temp_column_name] = pd.to_datetime(df[columns].mean(axis=1), errors='coerce')
        elif operation == "first":
            df[temp_column_name] = df[columns].bfill(axis=1).iloc[:, 0]
        else:
            raise ValueError(f"Operación '{operation}' no soportada para 'type'='Date'.")
    else:
        raise ValueError(f"Tipo '{type}' no soportado.")
    
    # Eliminar las columnas originales si se especifica drop=True
    if drop:
        df.drop(columns=columns, inplace=True)
    
    # Renombrar la columna temporal al nombre final deseado
    df.rename(columns={temp_column_name: name_column_new}, inplace=True)
    
    return df