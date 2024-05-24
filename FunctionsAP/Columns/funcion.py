import numpy as np

#Creando función de busqueda de valores no NaN
def funcion(x):
    return ' '.join([str(v) if isinstance(v, str) else np.nan for v in x.dropna().head(1)])
