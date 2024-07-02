import pandas as pd
import numpy as np

#Creando función para eliminar valores de una columna si otras no poseen valores
def eliminar_valor_columna1(df, Columna1, lista_columnas):
    mask = pd.Series(True, index=df.index)  # Inicializamos la máscara como True

    for columna in lista_columnas:
        mask = mask & df[columna].isna()  # Actualizamos la máscara con cada columna

    # Eliminamos cualquier valor en la 'Columna1' si la máscara es True
    df.loc[mask, Columna1] = np.nan

    return df
