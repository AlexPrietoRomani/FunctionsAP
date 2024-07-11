import numpy as np
import pandas as pd

def data_base_genetic(df, cycle = ["CI","CII", "CIII", "CIV"], index_column = [], column_calid = [], list_dic = {} ):
    
    # Obteniendo nombres de las columnas del dataframe
    list_columns = list(df.columns)
    
    #Creando lista de columnas que estan entre index y columnas calidad
    #Capturando posiciones en la lista de columnas
    posicion_inicial_calid = list_columns.index(column_calid[0])
    posición_final_calid = list_columns.index(column_calid[-1])
    posición_final_index = list_columns.index(index_column[-1])
    
    #Listas de columnas intermedias
    lista_inted = list_columns[int(posición_final_index+1):int(posicion_inicial_calid)]
    lista_final = list_columns[int(posición_final_calid+1):]
        
    if cycle == "CI":
        ######  Parte 1: Dataframe de data (concatenado)  ####################################
        # Realizando interelación de columnas de calidad con diccionarios
        for col, mapeo in list_dic.items():
            #Creando cariable para la nueva columna
            nueva_col = f'{col}_#'
            #Realizando columna de el calculado
            df[nueva_col] = df[col].apply(lambda x: mapeo.get(x, None))
        
        #Creamos Variable con columnas a sumar
        columnas_a_sumar = [f'{col}_#' for col in column_calid]

        #Reordenando columnas
        #Creando lista de lista de calidad categorica y numerica
        lista_intercalada_calidad = [item for pair in zip(column_calid, columnas_a_sumar) for item in pair]
        
        #Creando lista reordenada de las columnas
        orden_columnas = index_column + lista_inted + lista_intercalada_calidad + lista_final
        
        #Reordenando columnas
        df = df.reindex(columns = orden_columnas)
        
        #Función para sumar columnas de la variable
        df["Suma de puntaje"] = df[columnas_a_sumar].sum(axis=1,skipna=True)

        #Realizamos el conteo de las columnas a sumar omitiendo los vacios
        df["Traits evaluados"] = df[columnas_a_sumar].count(axis=1)

        #Cambiando los "0" por NaN
        df["Suma de puntaje"].replace(0, np.nan, inplace=True)
        df["Traits evaluados"].replace(0, np.nan, inplace=True)
        
        #Creando función que nos indica que se haya evaluado
        def columna_presente(df, columna, new_column):
            """
            Crea una columna que contenga un valor de 1 si existe un número en la columna especificada y 0 si es NaN o nulo.

            Args:
                df: El `DataFrame` en el que se creará la columna.
                columna: El nombre de la columna en la que se verificarán los valores.

            Returns:
                El `DataFrame` modificado con la nueva columna.
            """

            # Crea una nueva columna con el valor 1 por defecto.
            df[new_column] = 1

            # Reemplaza los valores NaN y nulos por 0.
            df[new_column] = df[new_column].where(df[columna].notnull(), 0)

            return df

        #Creando columna con los traits totles evaluados
        df["Puntos"] = len(columnas_a_sumar)

        #Creando la columna en base a la función creada
        df = columna_presente(df, 'Suma de puntaje','Evaluados')
        
        #Copiando df a un nuevo dataframe
        dataframe = df.copy()
        
        ######  Parte 2: Base de datos  ########################################################
        # Obteniendo nombres de las columnas del dataframe
        list_columns = list(df.columns)
        
        #Capturando posiciones en la lista de columnas
        posicion_inicial_calid = list_columns.index(lista_intercalada_calidad[0])
        posición_final_calid = list_columns.index(lista_intercalada_calidad[-1])
        posición_final_index = list_columns.index(index_column[-1])
        
        #Listas de columnas intermedias
        lista_inted = list_columns[int(posición_final_index+1):int(posicion_inicial_calid)]
        ## Quitando valores a lista_inted
        lista_inted.remove("Evaluación")
        lista_inted.remove("Semana")
        #Lista del final
        lista_final = list_columns[int(posición_final_calid+1):]
        
        #Definiendo columnas para repartir los pivot
        columnas_a_pivotear_1 = lista_inted + lista_intercalada_calidad[len(lista_intercalada_calidad)//2:]
        columnas_a_pivotear_2 = lista_intercalada_calidad[:len(lista_intercalada_calidad)//2] + lista_final
        columnas_a_pivotear = columnas_a_pivotear_1 + columnas_a_pivotear_2
        
        columnas_index = index_column.copy()

        data = df.copy()

        pivot_df_1 = pd.pivot_table(data= data,index=index_column, columns="Evaluación", values=columnas_a_pivotear_1, aggfunc="first")
        pivot_df_2 = pd.pivot_table(data= data,index=index_column, columns="Evaluación", values=columnas_a_pivotear_2, aggfunc="first")

        # Redefinir las columnas
        pivot_df_1.columns = [f"{col[0]}_CI-{col[1]}" for col in pivot_df_1.columns]
        pivot_df_2.columns = [f"{col[0]}_CI-{col[1]}" for col in pivot_df_2.columns]

        # Reiniciar el índice si deseas que "EVALUAR" sea una columna
        pivot_df_1 = pivot_df_1.reset_index()
        pivot_df_2 = pivot_df_2.reset_index()

        #Uniendo dataframes
        pivot_df = pd.merge(pivot_df_1, pivot_df_2, on=index_column, how="outer")
    
    return dataframe, pivot_df