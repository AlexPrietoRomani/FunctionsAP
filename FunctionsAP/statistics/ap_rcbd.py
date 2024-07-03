import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

class FieldLayout:
    def __init__(self, book):
        self.book = book

    def plot_book(self):
        plot_data = self.book

        # Crear un mapeo de genotipos a números
        genotypes = plot_data['genotipo'].unique()
        genotype_map = {genotype: idx for idx, genotype in enumerate(genotypes, 1)}

        # Crear una figura con subplots para cada bloque
        num_blocks = plot_data["bloque"].max()
        fig, axes = plt.subplots(1, num_blocks, figsize=(5 * num_blocks, 5))
        fig.suptitle("Field Layout", fontsize=16)

        for block in range(1, num_blocks + 1):
            block_data = plot_data[plot_data['bloque'] == block]

            # Crear una matriz para el heatmap con los números de genotipo
            matrix = np.full((plot_data['fila'].max(), plot_data['columna'].max()), np.nan)
            annotation_matrix = np.full((plot_data['fila'].max(), plot_data['columna'].max()), '', dtype=object)
            for _, row in block_data.iterrows():
                matrix[int(row['fila']) - 1, int(row['columna']) - 1] = genotype_map[row['genotipo']]
                annotation_matrix[int(row['fila']) - 1, int(row['columna']) - 1] = row['genotipo']

            # Dibujar el heatmap con los nombres de genotipo como anotaciones
            sns.heatmap(matrix, ax=axes[block - 1], cmap='Set1', cbar=False,
                        annot=annotation_matrix, fmt='', mask=np.isnan(matrix))

            axes[block - 1].set_title(f'Block {block}')
            axes[block - 1].set_xlabel('Column')
            if block == 1:
                axes[block - 1].set_ylabel('Row')
            else:
                axes[block - 1].set_yticks([])

        plt.tight_layout()
        plt.show()

def ap_rcbd(geno, nb, nc, variable_capacity=False, col_capacities=None,serpentine=True, alongside=['no', 'rows', 'columns']):
    """
    Crea un diseño de bloques completos al azar aumentado (Augmented RCBD).

    Parámetros:
    geno (list): Lista de genotipos.
    nb (int): Número de bloques.
    nc (int): Número de columnas.
    variable_capacity (bool): Si es True, se usan capacidades de columna variables.
    col_capacities (list): Lista de capacidades de columna cuando variable_capacity es True.
    serpentine (bool): Si es True, se usa un patrón serpentino para la numeración de parcelas.
    alongside (list): Opciones para la disposición de bloques ['no', 'rows', 'columns'].

    Retorna:
    dict: Un diccionario con 'plan' (el diseño del campo) y 'book' (el libro de campo).
    """
    
    # Validar argumentos
    if nb < 2:
        raise ValueError("Incluya al menos 2 bloques.")
    
    # Captura del número de genotipos propuestos
    ng = len(geno)
    
    # Verificación del número de genotipos dados en el diseño
    if ng < 2:
        raise ValueError("Incluya al menos 2 genotipos.")
    
    # Verificando argumento "alongside"
    alongside = alongside[0] if alongside[0] in ['no', 'rows', 'columns'] else 'no'
    
    # Manejar capacidad variable
    if variable_capacity:
        if col_capacities is None:
            raise ValueError("col_capacities debe proporcionarse cuando variable_capacity es True.")
        
        if len(col_capacities) != nc:
            raise ValueError("El número de capacidades de columna debe coincidir con el número de columnas.")
        
        if sum(col_capacities) < ng * nb:
            raise ValueError("La capacidad total de las columnas es menor que el número de parcelas necesarias.")
        
        max_rows = max(col_capacities)
    else:
        cols_per_block = nc // nb
        geno_per_col = -(-ng // cols_per_block)  # División con techo
        max_rows = geno_per_col
        col_capacities = [geno_per_col] * cols_per_block + [geno_per_col - 1] * (nc - cols_per_block)
        col_capacities = col_capacities[:nc]  # Asegurar que la longitud sea nc
    
    # Crear plan de campo
    plan = np.full((max_rows, nc, nb), None, dtype=object)
    
    # Incluir genotipos al azar
    for k in range(nb):
        sg = np.random.permutation(geno)
        geno_index = 0
        for j in range(nc):
            for i in range(col_capacities[j]):
                if geno_index < ng:
                    plan[i, j, k] = sg[geno_index]
                    geno_index += 1
    
    # Crear libro de campo
    book = pd.DataFrame(columns=['Plot', 'bloque', 'fila', 'columna', 'genotipo'])
    
    # Comienzo de la numeración del plot
    plot_counter = 1
    
    # Crear filas para el libro de campo
    for k in range(nb):
        for j in range(nc):
            for i in range(col_capacities[j]):
                if plan[i, j, k] is not None:
                    new_row = pd.DataFrame({
                        'Plot': [plot_counter],
                        'bloque': [k + 1],
                        'fila': [i + 1],
                        'columna': [j + 1],
                        'genotipo': [plan[i, j, k]]
                    })
                    book = pd.concat([book, new_row], ignore_index=True)
                    plot_counter += 1
    
    # Ordenar por número de parcela
    if serpentine and max_rows > 1:
        book = book.sort_values(['bloque', 'columna', 'fila'], 
                                key=lambda x: np.where(x.name == 'fila', 
                                                       np.where(book['columna'] % 2 == 0, -x, x), 
                                                       x))
    book.index = range(1, len(book) + 1)
    
    # Cambiar números de fila y columna si es necesario
    if alongside == "rows":
        new_plan = np.full((max_rows, nc * nb), None, dtype=object)
        for k in range(nb):
            new_plan[:, (k*nc):((k+1)*nc)] = plan[:, :, k]
        plan = new_plan
        book['columna'] = book['columna'] + (book['bloque'] - 1) * nc
    
    if alongside == "columns":
        new_plan = np.full((max_rows * nb, nc), None, dtype=object)
        for k in range(nb):
            new_plan[(k*max_rows):((k+1)*max_rows), :] = plan[:, :, k]
        plan = new_plan
        book['fila'] = book['fila'] + (book['bloque'] - 1) * max_rows
    
    # Retornar la instancia de FieldLayout
    return FieldLayout(book)