import pandas as pd

def modific_outlier(df, columnas, eliminar=False, coincidencia="all"):
    # Crear un diccionario para almacenar los índices de los outliers por columna
    outliers_indices = {}

    # Iterar sobre las columnas especificadas
    for column_name in columnas:
        # Extraer los datos de la columna
        column_data = df[column_name]

        # Calcular Q1, Q3 e IQR
        Q1 = column_data.quantile(0.25)
        Q3 = column_data.quantile(0.75)
        IQR = Q3 - Q1

        # Definir los límites para los outliers
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR

        # Detectar índices de outliers
        outliers = column_data[(column_data < lower_bound) | (column_data > upper_bound)].index

        # Guardar los índices de outliers en el diccionario
        outliers_indices[column_name] = outliers

        # Imprimir la cantidad de outliers detectados en la columna
        print(f"La columna {column_name} tiene {len(outliers)} outliers.")

    # Convertir el diccionario de índices de outliers en una matriz lógica
    filas_outliers_logicas = pd.DataFrame(False, index=df.index, columns=columnas)
    for column_name, indices in outliers_indices.items():
        filas_outliers_logicas.loc[indices, column_name] = True

    # Determinar las filas a eliminar según el argumento 'coincidencia'
    if coincidencia == "all":
        # Eliminar filas donde todas las columnas tienen outliers (intersección)
        filas_outliers = filas_outliers_logicas.all(axis=1)
    elif coincidencia == "any":
        # Eliminar filas donde al menos una columna tiene un outlier (unión)
        filas_outliers = filas_outliers_logicas.any(axis=1)
    elif coincidencia == "majority":
        # Eliminar filas donde más del 50% de las columnas tienen outliers
        filas_outliers = filas_outliers_logicas.sum(axis=1) > (len(columnas) / 2)
    else:
        raise ValueError("El valor de 'coincidencia' debe ser 'all', 'any' o 'majority'.")

    # Obtener los índices de las filas a eliminar
    filas_outliers_indices = df.index[filas_outliers]

    # Imprimir la cantidad de filas con outliers según el criterio de coincidencia
    print(f"Hay {len(filas_outliers_indices)} filas con outliers según el criterio de coincidencia: {coincidencia}.")

    if eliminar:
        # Eliminar las filas que coinciden según el criterio de 'coincidencia'
        df_sin_outliers = df.drop(filas_outliers_indices)

        # Imprimir cuántas filas serán eliminadas
        print(f"Se eliminarán {len(filas_outliers_indices)} filas que contienen outliers según el criterio de coincidencia: {coincidencia}.")

        return df_sin_outliers  # Retornar el DataFrame sin las filas con outliers
    else:
        # Solo retornar los índices de las filas con outliers sin eliminar
        return filas_outliers_indices  # Retornar los índices de las filas con outliers