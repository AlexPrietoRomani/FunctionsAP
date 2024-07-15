import pandas as pd
import numpy as np

#Creando funciones para suma de dos columnas de un dataframe
def columns_add(dataframe, columns, name_column_new, type = ["Number", "Text"], drop = True):
    
    """
      Concatena columnas ya sean de tipo texto o número.

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
        #Devolviendo columna nueva.
        df["CoL$&$umNa_칩CreADA"] = df[columns].sum(axis = 1)
         
    if type == "Text":
        
        #En caso alguna columna no sea tipo texto.      
        for column in columns:
          df[column] = df[column].astype(str)
        
        #En caso exista valores vacios en las columnas a unir, que estas queden como vacias.      
        for column in columns:
          df[column].replace("nan","", inplace=True)
        
        #En caso exista valores vacios en las columnas a unir, que estas queden como vacias.      
        for column in columns:
          df[column].fillna("",inplace=True)
        
        #Creando formula para poder sumar columnas indiferente cuantas columnas existan
        formula = "+".join(["df['" + column + "']" for column in columns])
        
        #Devolviendo columna nueva.
        df["CoL$&$umNa_칩CreADA"] = eval(formula)
        
    #Creando condicional para el argumento "drop"
    if drop == True:
      
      #Eliminando columnas utilizadas
      df.drop(columns = columns, inplace=True)
    
    #Cambiando nombre de la columna a la especificada según el argumento "name_column_new"
    df.rename(columns = {"CoL$&$umNa_칩CreADA":name_column_new}, inplace = True)
    
    # Retornando el dataframe  
    return df

  
