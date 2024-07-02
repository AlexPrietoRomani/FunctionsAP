import pandas as pd
import numpy as np

#Creando función de reemplazo de valores vacios con NaN
def reemplazar_valores(df,valor_original,valor_reemplazo):
    for col in df.columns:
        df[col] = df[col].replace(valor_original, valor_reemplazo)
    return df