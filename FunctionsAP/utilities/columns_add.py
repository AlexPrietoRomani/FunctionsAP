import pandas as pd
import numpy as np

#Creando funciones para suma de dos columnas de un dataframe
def columns_add(dataframe, columns, name_column_new, type="Number", drop=True, separator="", operation="sum"):
    
    """
    Concatena o suma columnas del DataFrame, ya sean de tipo texto o número.

    Parámetros:
      dataframe: DataFrame que se usará para la función.
      columns: Lista de nombres de columnas que se quiere agregar o sumar.
      name_column_new: Nombre de la columna nueva que se quiere crear.
      type: Tipo de las columnas que se quiere agregar o sumar ("Number" o "Text").
      drop: Booleano que indica si las columnas originales deben ser eliminadas (default=True).
      separator: Separador para concatenar texto (solo aplica si type="Text").
      operation: Operación aritmética a realizar (sum, mean, prod), solo para type="Number".

    Devuelve:
      Un DataFrame que contiene la columna nueva. Si se requiere, elimina las columnas originales.
    """
    # Validar que 'columns' sea una lista
    if not isinstance(columns, list):
        raise TypeError("El argumento 'columns' debe ser una lista de nombres de columnas.")

    # Validar el parámetro type
    if type.lower() not in ["number", "text"]:
        raise ValueError("El argumento 'type' debe ser 'Number' o 'Text'.")

    # Validar que todas las columnas existen en el DataFrame
    missing_columns = [col for col in columns if col not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"Las siguientes columnas no se encontraron en el DataFrame: {missing_columns}")

    # Copiar el DataFrame para no afectar el original
    df = dataframe.copy()

    # Definir un nombre temporal para evitar colisiones con columnas existentes
    temp_column_name = f"CoL$&$umNa_칩CreADA_{name_column_new}"

    if type.lower() == "number":
        # Realizar la operación aritmética especificada
        if operation == "sum":
            df[temp_column_name] = df[columns].sum(axis=1, skipna=True)
            df[temp_column_name] = df[temp_column_name].where(df[columns].notna().any(axis=1), np.nan)
        elif operation == "mean":
            df[temp_column_name] = df[columns].mean(axis=1, skipna=True)
            df[temp_column_name] = df[temp_column_name].where(df[columns].notna().any(axis=1), np.nan)
        elif operation == "prod":
            df[temp_column_name] = df[columns].prod(axis=1, skipna=True)
            df[temp_column_name] = df[temp_column_name].where(df[columns].notna().any(axis=1), np.nan)
        else:
            raise ValueError(f"Operación '{operation}' no soportada para columnas numéricas.")


    elif type.lower() == "text":
        # Concatenar columnas de texto con el separador especificado
        df[temp_column_name] = df[columns].astype(str).replace("nan", "").apply(lambda row: separator.join(row), axis=1)

    # Eliminar columnas originales si se especifica drop=True
    if drop:
        df.drop(columns=columns, inplace=True)

    # Cambiar el nombre de la columna temporal a la especificada según el argumento "name_column_new"
    if temp_column_name in df.columns:
        df.rename(columns={temp_column_name: name_column_new}, inplace=True)

    return df

  
