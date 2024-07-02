import pandas as pd
import zscore
import numpy as np

def modific_outlier(dataframe, columns, threshold):
    
    #Definiendo la función
    def clean_outliers(lista, threshold):
    
        #Seleccionando la columna 
        data = lista.copy()
        
        # Calculate z-score for each data point and compute its absolute value
        z_scores = zscore(data)
        
        #Capturando lista con los valores de zcore
        abs_z_scores = np.abs(z_scores)
        
        #Creando dataframe temporal
        df = pd.DataFrame({
        "valores": data,
        "zscore":abs_z_scores
        })

        # Seleccioón de los outliers con el threshold determinado por el usuario
        outliers = df.loc[df["zscore"] > threshold]

        # Calculate the median sin outliers
        median_value = df['valores'].loc[df["zscore"] < 1.5].median()

        # Imputando los valores de la media
        taxis_imputed = df.copy()

        #Cambiando los valores por la media calculada
        taxis_imputed.loc[outliers.index, 'valores'] = median_value

        #Eliminando columna del zscore
        taxis_imputed.drop(columns="zscore", inplace=True)

        #Cambiando a lista
        taxis_imputed = list(taxis_imputed["valores"])
        
        return taxis_imputed
    
    # Obtener la lista de índices
    indices = dataframe.index.tolist()
    
    for indice in indices:
        # Seleccionar los valores del índice en las columnas requeridas
        valores = dataframe.loc[indice, columns].values.tolist()
        
        #Usando la función antes predefinida
        valores_modificados = clean_outliers(valores, threshold)
        
        #Cambiando los valores del dataframe con los valores actualizados
        dataframe.loc[indice, columns] = valores_modificados
    
    #Retornando el dataframe modificado
    return dataframe