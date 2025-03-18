import pandas as pd
import numpy as np

# Función para rellenar valores faltantes según código
def handle_missing_data(
    self,
    columnas_a_evaluar: list,
    columna_codigo: str,
    columna_semana: str,
    mode: str = 'detect',
    method: str = 'moda',
    columnas_info: list = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Función para detección y/o relleno de datos faltantes según valores únicos y evaluaciones en un dataframe.

    Parámetros:
    -----------
    columnas_a_evaluar (list):
        Lista de columnas a verificar/llenar [[2]]
    columna_codigo (str):
        Columna con identificador único de registros [[6]]
    columna_semana (str):
        Columna que identifica evaluaciones/periodos [[6]]
    mode (str):
        'detect' para análisis de missing values, 'fill' para rellenar [[1]]
    method (str):
        Método de relleno ('moda', 'media', 'mediana') [[4]]
    columnas_info (list):
        Columnas adicionales a incluir en el resultado [[3]]
    verbose (bool):
        Mostrar mensajes de proceso (default: True)

    Retorna:
    --------
    - En modo 'detect': 
        pd.DataFrame con informe de valores faltantes
    - En modo 'fill': 
        pd.DataFrame con valores rellenados

    Errores:
    --------
    - ValueError por columnas inválidas
    - ValueError por modo inválido
    - ValueError por método de relleno inválido

    Ejemplo:
    --------
    >>> df_missing = df.handle_missing_data(cols, 'ID', 'Semana', mode='detect')
    >>> df_filled = df.handle_missing_data(cols, 'ID', 'Semana', mode='fill')
    """
    
    # Validaciones iniciales
    if mode not in ['detect', 'fill']:
        raise ValueError("El modo debe ser 'detect' o 'fill' [[1]]")
        
    required_cols = columnas_a_evaluar + [columna_codigo, columna_semana]
    if columnas_info:
        required_cols += columnas_info
        
    for col in required_cols:
        if col not in self.columns:
            raise ValueError(f"Columna faltante: {col} [[6]]")

    df_copy = self.copy()
    mask = df_copy[columnas_a_evaluar].applymap(lambda x: pd.isna(x) or x == '')
    filtered_mask = mask.any(axis=1) & ~mask.all(axis=1)

    if mode == 'detect':
        # Lógica de detección de missing values
        missing_cols = mask.loc[filtered_mask].apply(
            lambda row: [col for col in row.index if row[col]], 
            axis=1
        )
        
        info_cols = columnas_info + [columna_codigo, columna_semana] if columnas_info else [columna_codigo, columna_semana]
        result_df = df_copy.loc[filtered_mask, info_cols].copy()
        result_df['missing_columns'] = missing_cols
        result_df['missing_count'] = mask.sum(axis=1)
        
        return result_df

    elif mode == 'fill':
        # Lógica de relleno inteligente
        num_rellenadas = 0

        def fill_row(row):
            nonlocal num_rellenadas
            original_row = row.copy()
            
            for col in columnas_a_evaluar:
                if pd.isna(row[col]) or row[col] == '':
                    # Filtrar valores válidos del mismo código en otras semanas
                    filtro = (df_copy[columna_codigo] == row[columna_codigo]) & \
                            (df_copy[columna_semana] != row[columna_semana])
                            
                    valores = df_copy.loc[filtro, col].replace('', np.nan).dropna()
                    
                    if valores.empty:
                        continue  # Sin valores para rellenar [[2]]
                        
                    # Calcular estadístico según método
                    try:
                        if method == 'moda':
                            nuevo_valor = valores.mode()[0] if not valores.mode().empty else np.nan
                        elif method in ['media', 'mediana']:
                            valores_num = pd.to_numeric(valores, errors='raise')
                            nuevo_valor = getattr(valores_num, method)()
                        else:
                            raise ValueError(f"Método '{method}' no válido [[4]]")
                    except Exception as e:
                        print(f"Error en columna '{col}': {str(e)}")
                        continue

                    # Actualizar valor y conteo
                    if not pd.isna(nuevo_valor):
                        row[col] = nuevo_valor
                        if verbose:
                            print(f"Rellenado {col} para {columna_codigo}={row[columna_codigo]} con {nuevo_valor} [[3]]")
            
            if not original_row.equals(row):
                num_rellenadas += 1
            return row

        # Aplicar relleno y preparar salida
        df_filled = df_copy.copy()
        df_filled.loc[filtered_mask] = df_filled.loc[filtered_mask].apply(fill_row, axis=1)

        if verbose:
            print(f"\n--- Relleno completado ---")
            print(f"Filas modificadas: {num_rellenadas} [[5]]")
            print(f"Metodo utilizado: {method}")
        
        return df_filled