import pandas as pd
import numpy as np
import os
import openpyxl
import chardet
import re
from datetime import datetime

#Creando función para leer archivos csv de una carpeta. (Para dos espacios de fecha inicial)
def join_files(carpeta, column_types = None, time = False, type = [".csv", "xlsx"]):
  """
  Crea un DataFrame a partir de archivos CSV en una carpeta.

  Parámetros:
    carpeta: Ruta a la carpeta que contiene los archivos CSV.
    column_types: Diccionario en el cual se define de que tipos son las columnas al momento de la lectura. Este argumento queda como "None" por defecto.
    time: Argumento que indica si se requiere capturar la fecha del nombre de los archivos. Por defecto queda como False
    type: argumento en el cual se especifica que tipo de archivos va a colectar.
    
  Devuelve:
    Un DataFrame que contiene los datos de todos los archivos CSV en la carpeta.
  """
  #Condicional para el argumento "type"
  if type == ".csv":
  
    # Obtener una lista de los nombres de los archivos CSV en la carpeta
    archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.csv')]
  
  if type == ".xlsx":
  
    # Obtener una lista de los nombres de los archivos CSV en la carpeta
    archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.xlsx')]
    
  # Crear una lista para almacenar los DataFrames de cada archivo CSV
  dataframes = []

  #Condicional para el argumento "time"
  if time == True:

    for archivo in archivos_csv:
      ruta_archivo = os.path.join(carpeta, archivo)

      #Crear el patrón de la fecha
      pattern = r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}'

      #Generando la lectura del patrón "pattern" dentro del string "archivo"
      match = re.search(pattern, archivo)
      if match:
          date_str = match.group()
          if match:
                  date_str = match.group()
                  date_obj = datetime.strptime(date_str, "%Y-%m-%d-%H-%M-%S")  # Crear el objeto de fecha

    # Verifica si es un archivo regular (no un directorio)
    if os.path.isfile(ruta_archivo):
        try:
            # Abre el archivo en modo binario
            with open(ruta_archivo, 'rb') as f:
                # Lee los primeros bytes del archivo
                contenido = f.read()

            # Detecta la codificación del archivo
            resultado = chardet.detect(contenido)
            codificacion = resultado['encoding']

            # Imprime el nombre del archivo y su codificación
            #print(f'Archivo: {archivo}, Codificación: {codificacion}')
        except Exception as e:
            print(f'Error al procesar el archivo {archivo}: {e}')
            
    #Verificación si el argumento "column_types" queda como defecto
    if column_types is None:
        # Serie de pasos si column_types es None
        df = pd.read_csv(ruta_archivo, encoding = codificacion)

    else:
        # Serie de pasos si column_types tiene un valor
        df = pd.read_csv(ruta_archivo, dtype = column_types, encoding = codificacion)
    
    #Condicional para el argumento "time"
    if time == True:
      df['Fecha'] = date_obj  # Agregar la columna de fecha al DataFrame

    dataframes.append(df)

  # Concatenar los DataFrames en uno solo
  df_final = pd.concat(dataframes, ignore_index=True)

  return df_final
