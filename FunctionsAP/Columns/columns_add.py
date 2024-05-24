import pandas as pd
import numpy as np

#Creando funciones para suma de dos columnas de un dataframe
def columns_add(dataframe, columns, name_column_new, type = ["Number", "Text"], drop = True):
    
    """
      Crea un DataFrame a partir de archivos CSV en una carpeta.

      Parámetros:
        dataframe: Dataframe que se usará para la función.
        columns: Columnas que se quiera agregar o sumar.
        name_column_new: Nombre de la columna nueva que se quiere crear.
        type: Tipo de las columnas que se queiren agregar o sumar. Por defecto se queda como "float"
        drop: Argumento en el cual se especifica que los argumentos "columns" serán eliminados o no. Por defecto queda como "True"

      Devuelve:
        Un DataFrame en el cual se contiene la columna nueva. Si se requiere se elimina las anteriores.
    """
    
    #Copiando dataframe para no afectar a el dataframe final
    df = dataframe.copy()
    
    #Creando condicional para el argumento "type"
    if type == "Number":
        "" 
        #Devolviendo columna nueva con el nombre elegido por el usuario.
        df[name_column_new] = df[columns].sum(axis = 1)
         
    if type == "Text":
        
        #En caso exista valores vacios en las columnas a unir, que estas queden como vacias.      
        for column in columns:
          df[column].fillna("",inplace=True)
        
        #Creando formula para poder sumar columnas indiferente cuantas columnas existan
        formula = "+".join(["df['" + column + "']" for column in columns])
        
        #Devolviendo columna nueva con el nombre elegido por el usuario.
        df[name_column_new] = eval(formula)

    else:
        print("Error in argument: type; the possible arguments are Number or text")
        
    #Creando condicional para el argumento "drop"
    if drop == True:
      
      #Eliminando columnas utilizadas
      df.drop(columns = columns, inplace=True)
      
    # Retornando el dataframe  
    return df
  
