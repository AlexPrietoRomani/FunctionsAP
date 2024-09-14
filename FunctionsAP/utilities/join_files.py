import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime
from dateutil import parser
from dateutil.parser import ParserError
import pytz
import logging
from typing import List, Dict, Optional, Union

def join_files(
    folder_path: Union[str, Path],
    column_types: Optional[Dict[str, type]] = None,
    include_date: bool = False,
    file_extensions: Optional[List[str]] = None,
    default_timezone: str = 'UTC',
    encodings: Optional[List[str]] = None,
    stop_on_error: bool = False,
    chunksize: Optional[int] = None
) -> pd.DataFrame:
    """
    Crea un DataFrame a partir de archivos CSV o Excel en una carpeta.

    Parámetros:
        folder_path: Ruta a la carpeta que contiene los archivos.
        column_types: Diccionario que define los tipos de datos de las columnas al leer.
        include_date: Indica si se debe capturar la fecha del nombre de los archivos.
        file_extensions: Lista de extensiones de archivo a procesar. Por defecto es ['.csv', '.xlsx'].
        default_timezone: Zona horaria por defecto para las fechas.
        encodings: Lista de codificaciones a intentar al leer los archivos. Por defecto es ['utf-8', 'latin-1'].
        stop_on_error: Indica si el proceso debe detenerse al encontrar un error. Por defecto es False.
        chunksize: Número de filas a leer por iteración. Útil para archivos grandes. Por defecto es None.

    Devuelve:
        Un DataFrame que contiene los datos de todos los archivos en la carpeta.
    """
    # Configurar el logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if file_extensions is None:
        file_extensions = ['.csv', '.xlsx']

    if encodings is None:
        encodings = ['utf-8', 'latin-1']

    try:
        folder = Path(folder_path)
        if not folder.is_dir():
            logger.error(f"La ruta {folder_path} no es una carpeta válida.")
            return pd.DataFrame()

        # Obtener la lista de archivos con las extensiones especificadas
        file_list = [f for f in folder.iterdir() if f.suffix.lower() in file_extensions]

        num_files = len(file_list)

        if num_files == 0:
            logger.warning("No se encontraron archivos en la carpeta.")
            return pd.DataFrame()

        dataframes = []
        files_processed = 0

        for file_path in file_list:
            file_name = file_path.name

            # Verificar si es un archivo regular y no está vacío
            if not file_path.is_file():
                logger.warning(f"Saltando {file_name}, no es un archivo regular.")
                continue

            if file_path.stat().st_size == 0:
                logger.warning(f"El archivo {file_name} está vacío.")
                continue

            # Extraer la fecha del nombre del archivo si es necesario
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

            # Leer el archivo en un DataFrame
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

            # Agregar la fecha al DataFrame si se extrajo correctamente
            if include_date and date_obj:
                df['Fecha'] = date_obj

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
