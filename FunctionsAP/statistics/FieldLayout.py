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