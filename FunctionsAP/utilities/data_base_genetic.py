import numpy as np
import pandas as pd

def data_base_genetic(df, cycle = ["CI","CII", "CIII", "CIV"], index_column = [], column_calid = [], list_dic = {} ):
    """
    Procesa un DataFrame para generar un análisis genético de datos basado en evaluaciones y columnas de calidad.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos a procesar.
        cycle (str, optional): Ciclo de evaluación. El valor por defecto es "CI".
        index_column (list): Lista de columnas que se usarán como índice.
        column_calid (list): Lista de columnas de calidad a procesar.
        list_dic (dict): Diccionario de mapeo para las columnas de calidad, se encuentran los nombres de las columnas junto con sus diccionarios de equivalencia:

    Returns:
        tuple: Tupla con tres elementos:
            - dataframe (pd.DataFrame): DataFrame original con columnas reordenadas y nuevas columnas calculadas, solo es la concatenación con calculos
            - pivot_df (pd.DataFrame): DataFrame pivotado con columnas evaluadas.
            - resumen (pd.DataFrame): DataFrame con el resumen de los cálculos y análisis.
    Raises:
        TypeError: Si `index_column` no es una lista, `column_calid` no es una lista, o `list_dic` no es un diccionario.

    Example:
        >>> df = pd.DataFrame({
        ...     'Columna1': [1, 2, 3],
        ...     'Columna2': ["alto", "bajo", "bajo"],
        ...     'Columna3': ["grande", "chico", "grande"],
        ...     'Evaluación': [1, 2, 3]
        ... })
        >>> index_column = ['Columna1']
        >>> column_calid = ['Columna2', 'Columna3']
        >>> mapeo_Columna2 = {"alto":1,"bajo":0}
        >>> mapeo_Columna3 = {"grande":1,"chico":0}
        >>> list_dic = lista_diccionarios = {
            'Columna2': mapeo_Columna2,
            'Columna3': mapeo_Columna3}    
        >>> data_base_genetic(df, index_column=index_column, column_calid=column_calid, list_dic=list_dic)
    """
    # Manejo de errores para los tipos de argumentos
    if not isinstance(index_column, list):
        raise TypeError("index_column debe ser una lista.")
    if not isinstance(column_calid, list):
        raise TypeError("column_calid debe ser una lista.")
    if not isinstance(list_dic, dict):
        raise TypeError("list_dic debe ser un diccionario.")
    for key, value in list_dic.items():
        if not isinstance(value, dict):
            raise TypeError(f"El valor asociado a la clave '{key}' en list_dic debe ser un diccionario.")

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
        #Capturando columnas pivotadas
        columnas_a_pivotear = columnas_a_pivotear_1 + columnas_a_pivotear_2
        
        #Copiando index inicial
        index_column_copy = index_column.copy()
        
        #Copiando dataframe para realizar el pivoteo
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
        
        #Creando lista con los valores únicos de la columnas "Evaluación"
        evaluaciones = list(df["Evaluación"].unique())
        
        #Creando lista del orden de las columnas
        columnas_sin_index = [f"{columna}_CI-{eval}" for eval in evaluaciones for columna in columnas_a_pivotear]
        
        #Agregando index al orden de las columnas
        new_order = index_column_copy + columnas_sin_index
        
        #Reordenando columnas
        pivot_df = pivot_df.reindex(columns = new_order)
        
        ######  Parte 3: Resumen  ###############################################################
        #Aumentando lista del index 
        new_order = index_column.copy()

        #Iterando las columnas necesarias de el dataframe pivot_df
        for evaluación in evaluaciones:
            columnas = [f'Suma de puntaje_CI-{evaluación}', f'Traits evaluados_CI-{evaluación}', f'Puntos_CI-{evaluación}',f'Evaluados_CI-{evaluación}']
            new_order.extend(columnas)
            
        #Creando dataframe de la selección de columnas
        resumen = pivot_df[new_order]

        #Iterando columnas donde se reemplazaran valores
        for evaluación in evaluaciones:
            resumen[f'Suma de puntaje_CI-{evaluación}'].replace("",0, inplace=True)
            resumen[f'Traits evaluados_CI-{evaluación}'].replace("",np.nan, inplace=True)
        
        #Calculando el promedio ponderado:
        ## Creando columnas para el paso 1
        for evaluación in evaluaciones:
            resumen[f"Paso1_{evaluación}"] = resumen[f'Suma de puntaje_CI-{evaluación}']*resumen[f'Evaluados_CI-{evaluación}']

        ## Creando columnas para el paso 2 y 3
        resumen["Paso2"] = resumen[[f"Paso1_{evaluacion}" for evaluacion in evaluaciones]].sum(axis=1,skipna=True)
        resumen["Paso3"] = resumen[[f'Evaluados_CI-{evaluacion}' for evaluacion in evaluaciones]].sum(axis=1,skipna=True)

        # Creando columna del promedio ponderado
        resumen["Promedio total ponderado CI"] = resumen["Paso2"]/resumen["Paso3"]
        
        ## Eliminando columnas usadas para el proceso de promedio ponderado
        columnas_temporales = [f"Paso1_{evaluacion}" for evaluacion in evaluaciones] + ["Paso2", "Paso3"]
        resumen.drop(columns=columnas_temporales, inplace=True)

        #Calculando los puntos
        resumen["Ptos CI"] = resumen[[f"Puntos_CI-{evaluacion}" for evaluacion in evaluaciones]].mean(axis=1,skipna=True)

        #Creando columnas de Evaluados de la campaña
        resumen = columna_presente(resumen, "Promedio total ponderado CI",'Evaluados')

        #Creando columna de numero de evaluaciones de la campaña
        resumen["Numero de evaluaciones CI"] = resumen[[f"Traits evaluados_CI-{evaluacion}" for evaluacion in evaluaciones]].count(axis=1)
        
        #Iterando columnas donde se reemplazaran valores
        for evaluación in evaluaciones:
            resumen[f'Suma de puntaje_CI-{evaluación}'].replace(0,"se", inplace=True)
            resumen[f'Traits evaluados_CI-{evaluación}'].replace(np.nan,"se", inplace=True)

        # Realizando cambios en la columna de "Promedio total ponderado CI"
        resumen["Promedio total ponderado CI"].replace(0,"se", inplace=True)
        resumen["Promedio total ponderado CI"].replace(np.nan,"se", inplace=True)
        
    return dataframe, pivot_df, resumen