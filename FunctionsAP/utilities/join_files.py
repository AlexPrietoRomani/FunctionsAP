import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime
from dateutil import parser
from dateutil.parser import ParserError
import pytz
import logging
import unicodedata
from typing import List, Dict, Optional, Union

def join_files(
    folder_path: Union[str, Path],
    column_types: Optional[Dict[str, type]] = None,
    include_date: bool = False,
    date_column: str = 'Fecha',
    file_extensions: Optional[List[str]] = None,
    default_timezone: str = 'UTC',
    encodings: Optional[List[str]] = None,
    stop_on_error: bool = False,
    chunksize: Optional[int] = None,
    suffix_index: Optional[int] = None,
    suffix_delimiter: str = "_",
    suffix_filter: Optional[str] = None,
    normalize_columns: bool = False
) -> pd.DataFrame:
    """
    Crea un DataFrame a partir de archivos CSV o Excel en una carpeta.

    Parámetros:
        folder_path: Ruta a la carpeta que contiene los archivos.
        column_types: Diccionario que define los tipos de datos de las columnas al leer.
        include_date: Indica si se debe capturar la fecha del nombre de los archivos.
        date_column: Nombre de la columna donde se colocará la fecha extraída. Por defecto 'Fecha'.
        file_extensions: Lista de extensiones de archivo a procesar. Por defecto es ['.csv', '.xlsx'].
        default_timezone: Zona horaria por defecto para las fechas.
        encodings: Lista de codificaciones a intentar al leer los archivos. Por defecto es ['utf-8', 'latin-1'].
        stop_on_error: Indica si el proceso debe detenerse al encontrar un error.
        chunksize: Número de filas a leer por iteración (útil para archivos grandes).
        suffix_index: Si se especifica, extrae del nombre del archivo (sin extensión) el token en la posición dada al dividir por *suffix_delimiter*.
                      Ejemplo: -1 extrae el último token.
        suffix_delimiter: Delimitador a usar para separar el nombre del archivo. Por defecto "_".
        suffix_filter: Si se especifica, solo se leerán los archivos cuyo token extraído (usando suffix_index y suffix_delimiter)
                       sea igual a este valor (por ejemplo, "database").
        normalize_columns: Si es True, se realiza pre procesamiento de nombres de columnas, unificando columnas que sean iguales
                           ignorando mayúsculas, espacios y acentos.

    Devuelve:
        Un DataFrame que contiene los datos de todos los archivos en la carpeta que cumplen con los criterios.
    """
    # Configurar el logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Establecer extensiones y codificaciones por defecto si no se han pasado
    if file_extensions is None:
        file_extensions = ['.csv', '.xlsx']
    if encodings is None:
        encodings = ['utf-8', 'latin-1']

    try:
        folder = Path(folder_path)
        if not folder.is_dir():
            logger.error(f"La ruta {folder_path} no es una carpeta válida.")
            return pd.DataFrame()

        # Obtener la lista de archivos que tengan una de las extensiones especificadas
        file_list = [f for f in folder.iterdir() if f.suffix.lower() in file_extensions]
        num_files = len(file_list)
        if num_files == 0:
            logger.warning("No se encontraron archivos en la carpeta.")
            return pd.DataFrame()

        dataframes = []
        files_processed = 0

        for file_path in file_list:
            file_name = file_path.name

            # Verificar si es un archivo regular y que no esté vacío
            if not file_path.is_file():
                logger.warning(f"Saltando {file_name}, no es un archivo regular.")
                continue
            if file_path.stat().st_size == 0:
                logger.warning(f"El archivo {file_name} está vacío.")
                continue

            # Extraer la fecha del nombre del archivo si se solicita
            date_obj = None
            if include_date:
                try:
                    date_obj = extract_date_from_filename(file_name, default_timezone)
                except ParserError as e:
                    logger.error(f"Error al analizar la fecha en el archivo '{file_name}': {e}")
                    if stop_on_error:
                        raise
                    else:
                        continue
                except Exception as e:
                    logger.error(f"Ocurrió un error al extraer la fecha del archivo '{file_name}': {e}")
                    if stop_on_error:
                        raise
                    else:
                        continue

            # Extraer el sufijo del nombre del archivo si se especifica suffix_index
            add_suffix = False
            if suffix_index is not None:
                file_stem = file_path.stem  # Nombre sin extensión
                tokens = file_stem.split(suffix_delimiter)
                if len(tokens) > abs(suffix_index):
                    suffix_value = tokens[suffix_index]
                    # Si se especifica un filtro, solo procesamos si coincide
                    if suffix_filter is not None and suffix_value != suffix_filter:
                        logger.info(f"Saltando {file_name}: token '{suffix_value}' no coincide con el filtro '{suffix_filter}'.")
                        continue
                    add_suffix = True
                else:
                    logger.warning(f"No se pudo extraer el sufijo con índice {suffix_index} del archivo {file_name}.")

            # Intentar leer el archivo en un DataFrame
            try:
                df = read_file(
                    file_path=file_path,
                    column_types=column_types,
                    encodings=encodings,
                    chunksize=chunksize
                )
            except Exception as e:
                logger.error(f"Error al leer el archivo {file_name}: {e}")
                if stop_on_error:
                    raise
                else:
                    continue

            # Preprocesar los nombres de columnas si se solicita
            if normalize_columns:
                df = normalize_and_merge_columns(df)

            # Agregar la fecha extraída, si corresponde, y convertirla a datetime sin zona horaria
            if include_date and date_obj:
                df[date_column] = date_obj.replace(tzinfo=None)

            # Agregar el sufijo extraído al DataFrame, si corresponde
            if add_suffix:
                df['Suffix'] = suffix_value

            dataframes.append(df)
            files_processed += 1

        if dataframes:
            df_final = pd.concat(dataframes, ignore_index=True)
            logger.info(f"Se leyeron correctamente {files_processed} de {num_files} archivos.")
            return df_final
        else:
            logger.warning("No se pudieron crear DataFrames a partir de los archivos.")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Ocurrió un error inesperado: {e}")
        raise

def extract_date_from_filename(file_name: str, default_timezone: str) -> datetime:
    """
    Extrae la fecha del nombre de un archivo.

    Parámetros:
        file_name: Nombre del archivo.
        default_timezone: Zona horaria por defecto.

    Devuelve:
        Un objeto datetime con la fecha extraída.
    """
    # Expresiones regulares para diferentes formatos de fecha
    date_patterns = [
        r'\d{4}[-/]\d{2}[-/]\d{2}(?:[-_\s]\d{2}[:]\d{2}[:]\d{2})?',  # YYYY-MM-DD[-HH:MM:SS]
        r'\d{8}',  # YYYYMMDD
        r'\d{4}[-/]\d{3}'  # YYYY-DDD (día juliano)
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, file_name)
        if matches:
            date_str = matches[0]
            # Reemplazar separadores para estandarizar
            date_str = re.sub(r'[_\s]', '-', date_str)
            date_str = re.sub(r'[:]', '-', date_str)
            try:
                date_obj = parser.parse(date_str)
                if date_obj.tzinfo is None:
                    timezone = pytz.timezone(default_timezone)
                    date_obj = timezone.localize(date_obj)
                return date_obj
            except ParserError:
                continue  # Intentar con el siguiente patrón

    raise ParserError(f"No se encontró una fecha válida en el nombre del archivo '{file_name}'.")

def read_file(
    file_path: Path,
    column_types: Optional[Dict[str, type]],
    encodings: List[str],
    chunksize: Optional[int]
) -> pd.DataFrame:
    """
    Lee un archivo CSV o Excel en un DataFrame.

    Parámetros:
        file_path: Ruta al archivo.
        column_types: Diccionario de tipos de datos para las columnas.
        encodings: Lista de codificaciones a intentar.
        chunksize: Número de filas a leer por iteración.

    Devuelve:
        Un DataFrame con los datos del archivo.
    """
    file_name = file_path.name
    for encoding in encodings:
        try:
            if file_path.suffix.lower() == '.csv':
                if chunksize:
                    df = pd.read_csv(
                        file_path,
                        dtype=column_types,
                        encoding=encoding,
                        chunksize=chunksize
                    )
                    # Si se usa chunksize, concatenar los chunks
                    df = pd.concat(df, ignore_index=True)
                else:
                    df = pd.read_csv(
                        file_path,
                        dtype=column_types,
                        encoding=encoding
                    )
            elif file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(
                    file_path,
                    dtype=column_types
                )
            else:
                raise ValueError(f"Tipo de archivo no soportado para {file_name}.")
            # Si se leyó correctamente, salir del bucle
            return df
        except (UnicodeDecodeError, ValueError) as e:
            logging.warning(f"Error al leer {file_name} con codificación {encoding}: {e}")
            continue  # Intentar con la siguiente codificación
    
    # Si ninguna codificación funcionó, lanzar excepción
    raise ValueError(f"No se pudo leer el archivo {file_name} con las codificaciones proporcionadas.")

def remove_accents(input_str: str) -> str:
    """
    Elimina los acentos de la cadena de caracteres.
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_and_merge_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los nombres de las columnas eliminando espacios al inicio y al final,
    removiendo acentos, convirtiendo a minúsculas (para comparar) y unificando columnas
    que resulten iguales tras la normalización. El nombre final tendrá la primera letra en mayúscula.

    Parámetros:
        df: DataFrame original.

    Devuelve:
        Un nuevo DataFrame con los nombres de columnas normalizados y columnas duplicadas fusionadas.
    """
    # Crear un mapeo: nombre original -> nombre normalizado
    normalized_map = {col: remove_accents(col.strip()).lower().capitalize() for col in df.columns}
    
    # Invertir el mapeo para agrupar columnas que se normalizan igual
    groups = {}
    for original, norm in normalized_map.items():
        groups.setdefault(norm, []).append(original)
    
    new_df = pd.DataFrame(index=df.index)
    for norm_name, cols in groups.items():
        if len(cols) == 1:
            new_df[norm_name] = df[cols[0]]
        else:
            # Fusionar columnas: para cada fila, tomar el primer valor no nulo de las columnas duplicadas
            new_df[norm_name] = df[cols].bfill(axis=1).iloc[:, 0]
    return new_df
