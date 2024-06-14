import pandas as pd
import numpy as np
import os
import openpyxl
import chardet
import re
from datetime import datetime

#Creando función para leer archivos csv de una carpeta. (Para dos espacios de fecha inicial)
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
  
  try:
  
    #Condicional para el argumento "type"
    if type == ".csv":
    
      # Obtener una lista de los nombres de los archivos CSV en la carpeta
      archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.csv')]
    
    if type == ".xlsx":
    
      # Obtener una lista de los nombres de los archivos CSV en la carpeta
      archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.xlsx')]
  
  
    #Guardando cuantos archivos existen en la carpeta
    num_archivos = len(archivos_csv)
    
    #Verificar si no hay archivos:
    if num_archivos == 0:
      print("No existen archivos en la carpeta")
    else:
      #Variable ejecutados para guardar número de archivos leidos correctamente
      ejecutados = 0
      
      # Crear una lista para almacenar los DataFrames de cada archivo CSV
      dataframes = []

      #Creando iteración sobre la lista de archivos a extraer
      for archivo in archivos_csv:

        #Tomando la ruta del archivo de la lista
        ruta_archivo = os.path.join(carpeta, archivo)
        
        #Condicional para el argumento "time"
        if time == True:
            
            #Función para exepciones de errores
            try:
              #Crear el patrón de la fecha
              pattern = r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}'

              #Generando la lectura del patrón "pattern" dentro del string "archivo"
              match = re.search(pattern, archivo)
              if match:
                  
                  #En caso no exista error en el analisis de la fecha
                  try:
                    date_str = match.group()
                    
                    if match:
                            date_str = match.group()
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d-%H-%M-%S")  # Crear el objeto de fecha
                  
                  #Valor en caso de error sobre el analisis de la fecha
                  except Exception as ve:
                    
                    #Imprimiento texto en caso de error
                    print(f"Error al analizar la fecha '{date_str}' en el archivo '{archivo}': {ve}")
            
            #En caso de error sobre el argumento "time"       
            except Exception as e:
              print(f"Ha ocurrido un error procesando el archivo '{archivo}': {e}")
            
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
                
        # Verificar si el archivo está vacío 
        if os.path.getsize(ruta_archivo) == 0:
          
          #Imprimir texto si el archivo se encuentra vacio
          print((f'El archivo {ruta_archivo} está vacío.'))
        
        #Verificación si el argumento "column_types" queda como defecto
        if column_types is None:
          try:
            # Serie de pasos si column_types es None
            df = pd.read_csv(ruta_archivo, encoding = codificacion)
          except Exception as e:
            print(f'Error al procesar el archivo {archivo}: {e}')
        else:
          try:
            # Serie de pasos si column_types tiene un valor
            df = pd.read_csv(ruta_archivo, dtype = column_types, encoding = codificacion)
          except Exception as e:
            print(f'Error al procesar el archivo {archivo}: {e}')

          
        #Condicional para el argumento "time"
        if time == True:
            df['Fecha'] = date_obj  # Agregar la columna de fecha al DataFrame

        dataframes.append(df)
        
        if archivo:  # Verifica que el archivo no esté vacío
          ejecutados += 1  # Agrega el archivo a la lista
      
      # Concatenar los DataFrames en uno solo
      df_final = pd.concat(dataframes, ignore_index=True)

      print(f"Fueron leidos el {round(ejecutados/num_archivos*100, 1)}%")
      
      return df_final
  
  except Exception as e:
    print("No existe un archivo con la ruta: " + carpeta)