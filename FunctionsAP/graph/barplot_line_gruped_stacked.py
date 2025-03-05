import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np

def barplot_line_grouped_stacked(
    df: pd.DataFrame,
    group_col: str = "Codigo de Segregante",  # Columna para agrupar (por ejemplo, códigos)
    x_col: str = "Semana",                     # Columna para el eje x
    stacked_cols: list = None,                 # Lista de columnas para las barras apiladas
    orden_deseado: list = None,                # Orden deseado para los grupos (si se especifica)
    x_exclude: list = None,                    # Lista de valores a excluir en el eje x (por ejemplo, [46])
    line_cols: list = None,                    # Lista de columnas para graficar líneas (puede ser 1, 2 o 3)
    figsize: tuple = (15, 8),
    wspace: float = 0.1,
    save_fig: bool = False,
    fig_path: str = None,
    stacked_colors: list = None,               # Colores para las barras apiladas
    line_colors: list = None                   # Colores para las líneas (si hay más de una)
) -> None:
    """
    Crea un gráfico con subplots para cada grupo definido en 'group_col'.
    
    Para cada grupo, se grafican:
      - Barras apiladas usando las columnas indicadas en 'stacked_cols'.
      - Una o más líneas (con scatter) usando las columnas indicadas en 'line_cols'.
    
    Parámetros:
      - df (pd.DataFrame): DataFrame con los datos.
      - group_col (str): Nombre de la columna para agrupar. Por defecto "Codigo de Segregante".
      - x_col (str): Nombre de la columna para el eje x. Por defecto "Semana".
      - stacked_cols (list): Lista de nombres de columnas para las barras apiladas. 
          Ejemplo: ["% <=16mm", "% 16-17.9mm", "% 18-19.9mm", "% >=20mm"].
      - orden_deseado (list): Lista de valores para el grupo en el orden deseado. Se verifica que existan en 'group_col'.
      - x_exclude (list): Lista de valores a excluir en el eje x (por ejemplo, [46]). Por defecto None.
      - line_cols (list): Lista de columnas para graficar las líneas. Si no se especifica, no se grafican líneas.
      - figsize (tuple): Tamaño de la figura (anchura, altura). Por defecto (15, 8).
      - wspace (float): Espacio horizontal entre subplots. Por defecto 0.1.
      - save_fig (bool): Si es True, guarda la figura en 'fig_path'.
      - fig_path (str): Ruta donde se guarda la figura, si save_fig es True.
      - stacked_colors (list): Lista de colores para las barras apiladas. Si no se especifica, se usan colores por defecto.
      - line_colors (list): Lista de colores para las líneas. Si no se especifica, se usan 'black' para cada línea.
    
    Ejemplo de uso:
        orden = ['Csol18.148.116','Csol18.164.318','Csol18.113.46','T2']
        stacked = ["% <=16mm", "% 16-17.9mm", "% 18-19.9mm", "% >=20mm"]
        line_vars = ["Peso de baya (g)"]  # O puede ser más de una columna
        barplot_line_grouped_stacked(df, group_col="Codigo de Segregante", x_col="Semana",
                                     stacked_cols=stacked, orden_deseado=orden, x_exclude=[46],
                                     line_cols=line_vars, figsize=(15,8))
    """
    try:
        # Verificar que las columnas necesarias existan
        for col in [group_col, x_col]:
            if col not in df.columns:
                raise ValueError(f"La columna '{col}' no se encuentra en el DataFrame.")
        if stacked_cols is None or len(stacked_cols) == 0:
            raise ValueError("Debe especificar al menos una columna para las barras apiladas en 'stacked_cols'.")
        for col in stacked_cols:
            if col not in df.columns:
                raise ValueError(f"La columna de barras apiladas '{col}' no se encuentra en el DataFrame.")
        if line_cols is not None:
            for col in line_cols:
                if col not in df.columns:
                    raise ValueError(f"La columna de línea '{col}' no se encuentra en el DataFrame.")
        
        # Extraer los grupos disponibles en el DataFrame
        grupos = df[group_col].unique()
        
        # Verificar y ordenar según 'orden_deseado'
        if orden_deseado is not None:
            # Solo conservar aquellos valores que se encuentren en el DataFrame
            orden = [g for g in orden_deseado if g in grupos]
            # Agregar al final los grupos restantes (ordenados alfabéticamente)
            otros = sorted([g for g in grupos if g not in orden])
            configuraciones = orden + otros
        else:
            configuraciones = sorted(grupos)
        
        # Verificar que configuraciones no esté vacío
        if len(configuraciones) == 0:
            raise ValueError("No se encontraron valores en la columna de agrupación.")
        
        # Calcular el máximo global para las líneas (si se definen) para fijar el límite del eje y principal.
        if line_cols is not None and len(line_cols) > 0:
            global_max = max(df[col].max() for col in line_cols if pd.api.types.is_numeric_dtype(df[col]))
        else:
            # Si no se definen líneas, se puede usar el máximo de la primera columna de barras (aunque se espera que sean porcentajes)
            global_max = df[stacked_cols[0]].max()
        
        # Definir colores por defecto para las barras apiladas (se ajusta la cantidad)
        default_colors = ['#6C8EBF', '#D6A461', '#82B366', '#B4666E', '#8E44AD', '#3498DB']
        if stacked_colors is None:
            # Si hay más columnas que colores predeterminados, se extiende la paleta
            if len(stacked_cols) > len(default_colors):
                # Generar colores usando un colormap de matplotlib
                cmap = plt.get_cmap('tab20')
                stacked_colors = [cmap(i) for i in range(len(stacked_cols))]
            else:
                stacked_colors = default_colors[:len(stacked_cols)]
        
        # Definir colores para las líneas
        if line_cols is None or len(line_cols) == 0:
            line_colors = []
        else:
            if line_colors is None or len(line_colors) < len(line_cols):
                # Si no se proveen suficientes colores, usar 'black' para cada línea
                line_colors = ['black'] * len(line_cols)
        
        # Crear la figura y los subplots
        fig, axs = plt.subplots(1, len(configuraciones), figsize=figsize)
        plt.subplots_adjust(wspace=wspace)
        
        # Lista para la leyenda (se creará en el primer subplot)
        legend_elements = []
        
        # Iterar sobre cada grupo según el orden configurado
        for idx, grupo in enumerate(configuraciones):
            # Filtrar datos para el grupo actual
            try:
                df_filtrado = df[df[group_col] == grupo].copy()
                # Excluir valores del eje x si se especifica
                if x_exclude is not None:
                    df_filtrado = df_filtrado[~df_filtrado[x_col].isin(x_exclude)]
                df_filtrado.sort_values(by=x_col, inplace=True)
                # Convertir el eje x a string (útil para etiquetas)
                df_filtrado[x_col] = df_filtrado[x_col].astype(str)
            except Exception as e:
                print(f"Error al filtrar datos para el grupo '{grupo}': {e}")
                continue
            
            # Obtener el eje principal para el grupo (si solo hay un subplot, axs no es una lista)
            ax1 = axs[idx] if len(configuraciones) > 1 else axs
            # Crear eje secundario para las barras (stacked)
            ax2 = ax1.twinx()
            
            # Asegurarse de que el eje de líneas (ax1) se dibuje por encima del eje de barras (ax2)
            ax1.set_zorder(ax2.get_zorder() + 1)
            ax1.patch.set_visible(False)
            
            # Configurar límites de ejes:
            ax2.set_ylim(0, 100)  # Los porcentajes siempre entre 0 y 100
            ax1.set_ylim(0, global_max * 1.2)
            
            # Graficar las barras apiladas en ax2
            cumulative = np.zeros(len(df_filtrado))
            for i, col in enumerate(stacked_cols):
                try:
                    values = df_filtrado[col].values
                    ax2.bar(df_filtrado[x_col], values, bottom=cumulative, color=stacked_colors[i])
                    cumulative += values
                except Exception as e:
                    print(f"Error graficando la columna '{col}' en el grupo '{grupo}': {e}")
                    continue
            
            # Graficar las líneas (y scatter) en ax1 para cada columna especificada
            if line_cols is not None:
                for j, col in enumerate(line_cols):
                    try:
                        ax1.plot(df_filtrado[x_col], df_filtrado[col],
                                 color=line_colors[j], marker='o', markersize=5, linewidth=2, zorder=10, label=col)
                        ax1.scatter(df_filtrado[x_col], df_filtrado[col],
                                    color=line_colors[j], s=50, zorder=11)
                    except Exception as e:
                        print(f"Error graficando la línea para la columna '{col}' en el grupo '{grupo}': {e}")
                        continue
            
            # Configurar etiquetas y títulos
            ax1.set_title(f"{grupo}", fontsize=16, pad=15)
            ax1.set_xlabel(x_col, fontsize=16)
            if idx == 0:
                ax1.set_ylabel(line_cols[0] if (line_cols is not None and len(line_cols) > 0) else "Valor", fontsize=16, labelpad=10)
            else:
                ax1.set_ylabel("")
                ax1.tick_params(axis='y', labelleft=False)
            
            if idx == len(configuraciones) - 1:
                ax2.set_ylabel('%', fontsize=16, labelpad=10)
            else:
                ax2.set_ylabel("")
                ax2.tick_params(axis='y', labelright=False)
            
            ax1.tick_params(axis='x', labelsize=12, rotation=0)
            ax1.tick_params(axis='y', labelsize=14)
            ax2.tick_params(axis='y', labelsize=14)
            
            # Construir la leyenda reactiva solo en el primer subplot
            if idx == 0:
                # Leyenda para las barras
                legend_elements_bars = [
                    Line2D([0], [0], marker='s', color='w', markerfacecolor=stacked_colors[i],
                           markersize=12, label=col, linewidth=0) for i, col in enumerate(stacked_cols)
                ]
                # Leyenda para las líneas
                legend_elements_lines = []
                if line_cols is not None:
                    for j, col in enumerate(line_cols):
                        legend_elements_lines.append(
                            Line2D([0], [0], marker='o', color=line_colors[j],
                                   markersize=5, linewidth=2, label=col)
                        )
                legend_elements = legend_elements_bars + legend_elements_lines
                
        # Añadir leyenda global a la figura
        fig.legend(handles=legend_elements,
                   loc='upper right',
                   bbox_to_anchor=(1.12, 0.85),
                   fontsize=14,
                   title_fontsize=16)
        
        # Ajustar márgenes generales y mostrar o guardar la figura
        plt.subplots_adjust(left=0.05, right=0.92, top=0.85, bottom=0.15)
        if save_fig and fig_path:
            plt.savefig(fig_path)
        plt.show()
    
    except Exception as e:
        print(f"Error generando el gráfico: {e}")