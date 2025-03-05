import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional

def procesar_valores(
    df: pd.DataFrame,
    replace_map: dict = None,
    columnas: list = None,
    convertir_vacios: bool = False,
    fill_missing: bool = False,
    fill_value = None,
    convertir_tipo: Optional[Dict[str, type]] = None,
    trim_strings: bool = False,
    raise_error: bool = False
) -> pd.DataFrame:
    """
    Procesa y limpia los valores de un DataFrame de forma modular.
    
    Funcionalidades incluidas:
      1. Reemplazar valores según un diccionario (replace_map). Si se especifica 'columnas',
         se aplica solo a esas columnas; de lo contrario, se aplica a todas.
      2. Convertir valores "vacíos" (como '', ' ', 'nan', 'None' o None) a np.nan.
      3. Rellenar valores faltantes (NaN) con un valor especificado.
      4. Convertir el tipo de datos de columnas específicas, según un diccionario {columna: tipo}.
      5. Eliminar espacios en blanco (trim) en columnas de texto.
    
    Parámetros:
      - df (pd.DataFrame): DataFrame a procesar.
      - replace_map (dict, opcional): Diccionario con {valor_original: valor_reemplazo}.
      - columnas (list, opcional): Lista de nombres de columnas a procesar. Si es None, se aplica a todas.
      - convertir_vacios (bool): Si True, convierte ciertos valores "vacíos" a np.nan.
      - fill_missing (bool): Si True, rellena los valores faltantes con fill_value.
      - fill_value: Valor para rellenar NaN si fill_missing es True.
      - convertir_tipo (dict, opcional): Diccionario con {columna: tipo} para convertir el tipo de datos.
      - trim_strings (bool): Si True, elimina espacios en blanco iniciales y finales en columnas de texto.
      - raise_error (bool): Si True, se relanza la excepción en caso de error; de lo contrario, se registra y continúa.
    
    Retorna:
      - pd.DataFrame: DataFrame modificado con los valores procesados.
    
    Ejemplos:
        # Ejemplo 1: Reemplazar en todas las columnas los valores 0 por np.nan.
        # df_limpio = procesar_valores(df, replace_map={0: np.nan}, convertir_vacios=False)

        # Ejemplo 2: Solo en las columnas "A" y "B", convertir cadenas vacías y "None" a np.nan, y eliminar espacios.
        # df_limpio2 = procesar_valores(df, columnas=["A", "B"], convertir_vacios=True, trim_strings=True)

        # Ejemplo 3: En todas las columnas, convertir vacíos a np.nan, rellenar NaN con 0, y convertir la columna "edad" a entero.
        # df_limpio3 = procesar_valores(df, convertir_vacios=True, fill_missing=True, fill_value=0, convertir_tipo={"edad": int})
    """
    # Configurar logger básico
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Hacer una copia para no modificar el DataFrame original
        df_proc = df.copy()
    except Exception as e:
        logger.error(f"Error al copiar el DataFrame: {e}")
        if raise_error:
            raise
        return df

    # Determinar las columnas a procesar
    if columnas is None:
        columnas = df_proc.columns.tolist()
    else:
        # Filtrar las columnas que existan en el DataFrame
        columnas = [col for col in columnas if col in df_proc.columns]
    
    # 1. Reemplazar valores según replace_map
    if replace_map is not None and isinstance(replace_map, dict):
        for col in columnas:
            try:
                df_proc[col] = df_proc[col].replace(replace_map)
            except Exception as e:
                logger.error(f"Error reemplazando valores en la columna {col}: {e}")
                if raise_error:
                    raise

    # 2. Convertir valores "vacíos" a np.nan
    if convertir_vacios:
        valores_vacios = ["", " ", "nan", "None", None]
        for col in columnas:
            try:
                df_proc[col] = df_proc[col].replace(valores_vacios, np.nan)
            except Exception as e:
                logger.error(f"Error al convertir valores vacíos en la columna {col}: {e}")
                if raise_error:
                    raise

    # 3. Rellenar valores faltantes (NaN) si se solicita
    if fill_missing:
        try:
            df_proc = df_proc.fillna(fill_value)
        except Exception as e:
            logger.error(f"Error al rellenar valores faltantes: {e}")
            if raise_error:
                raise

    # 4. Convertir el tipo de datos de columnas específicas, si se proporciona convertir_tipo
    if convertir_tipo is not None and isinstance(convertir_tipo, dict):
        for col, new_type in convertir_tipo.items():
            if col in df_proc.columns:
                try:
                    df_proc[col] = df_proc[col].astype(new_type)
                except Exception as e:
                    logger.error(f"Error al convertir la columna {col} a {new_type}: {e}")
                    if raise_error:
                        raise
            else:
                logger.warning(f"La columna {col} no se encontró para conversión de tipo.")

    # 5. Eliminar espacios en blanco en columnas de texto si se solicita
    if trim_strings:
        for col in columnas:
            # Solo aplicar a columnas de tipo objeto (cadena)
            if pd.api.types.is_string_dtype(df_proc[col]):
                try:
                    df_proc[col] = df_proc[col].str.strip()
                except Exception as e:
                    logger.error(f"Error al aplicar trim en la columna {col}: {e}")
                    if raise_error:
                        raise

    return df_proc