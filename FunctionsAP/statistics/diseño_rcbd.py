import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

class FieldLayout:
    def __init__(self, book, plan):
        self.book = book
        self.plan = plan  # Agregamos el plan al objeto

    def plot_book(self):
        plot_data = self.book.copy()

        # Crear un mapeo de genotipos a números
        genotypes = plot_data['genotipo'].unique()
        genotype_map = {genotype: idx for idx, genotype in enumerate(genotypes, 1)}

        # Obtener el número de bloques
        num_blocks = plot_data["bloque"].nunique()

        # Crear una figura con subplots para cada bloque
        if num_blocks == 1:
            fig, axes = plt.subplots(1, 1, figsize=(6, 6))
            axes = [axes]  # Convertir a lista para iterar
        else:
            fig, axes = plt.subplots(1, num_blocks, figsize=(6 * num_blocks, 6))
            axes = axes.flatten()

        fig.suptitle("Diseño de Campo", fontsize=16)

        for idx, block in enumerate(sorted(plot_data['bloque'].unique())):
            block_data = plot_data[plot_data['bloque'] == block]

            max_row = block_data['fila'].max()
            max_col = block_data['columna'].max()

            # Crear una matriz para el heatmap con los números de genotipo
            matrix = np.full((max_row, max_col), np.nan)
            annotation_matrix = np.full((max_row, max_col), '', dtype=object)

            for _, row in block_data.iterrows():
                r = int(row['fila']) - 1
                c = int(row['columna']) - 1
                matrix[r, c] = genotype_map[row['genotipo']]
                annotation_matrix[r, c] = row['genotipo']

            # Dibujar el heatmap con los nombres de genotipo como anotaciones
            sns.heatmap(matrix, ax=axes[idx], cmap='Set3', cbar=False,
                        annot=annotation_matrix, fmt='', mask=np.isnan(matrix),
                        xticklabels=range(1, max_col + 1), yticklabels=range(1, max_row + 1))

            axes[idx].set_title(f'Bloque {block}')
            axes[idx].set_xlabel('Columna')
            axes[idx].set_ylabel('Fila')

        plt.tight_layout()
        plt.show()

    def verificacion_rcbd(self):
        """
        Verifica la estructura del diseño RCBD utilizando el libro de campo (layout.book).

        Retorna:
            dict: Diccionario con información sobre la calidad y validez del diseño.
        """

        book = self.book.copy()

        # Verificar que cada genotipo aparece exactamente una vez por bloque
        genotipos = book['genotipo'].unique()
        bloques = book['bloque'].unique()

        problemas_genotipos = []
        for bloque in bloques:
            book_bloque = book[book['bloque'] == bloque]
            conteo_genotipos = book_bloque['genotipo'].value_counts()

            # Verificar genotipos faltantes o repetidos en el bloque
            genotipos_faltantes = set(genotipos) - set(conteo_genotipos.index)
            genotipos_repetidos = conteo_genotipos[conteo_genotipos > 1].index.tolist()

            if genotipos_faltantes:
                problemas_genotipos.append({
                    'bloque': bloque,
                    'genotipos_faltantes': genotipos_faltantes
                })

            if genotipos_repetidos:
                problemas_genotipos.append({
                    'bloque': bloque,
                    'genotipos_repetidos': genotipos_repetidos
                })

        # Verificar si hay parcelas duplicadas en la misma fila y columna dentro del mismo bloque
        duplicates_within_block = book.duplicated(subset=['bloque', 'fila', 'columna'], keep=False)
        duplicados_within_block = book[duplicates_within_block]

        # Verificar si el mismo genotipo aparece en la misma posición en diferentes bloques
        duplicates_across_blocks = book.duplicated(subset=['fila', 'columna', 'genotipo'], keep=False)
        duplicados_across_blocks = book[duplicates_across_blocks]

        # Filtrar para obtener solo los duplicados que ocurren en diferentes bloques
        duplicados_across_blocks = duplicados_across_blocks.groupby(['fila', 'columna', 'genotipo']).filter(lambda x: x['bloque'].nunique() > 1)

        # Verificar balance de genotipos en filas y columnas
        balance_filas = book.groupby('fila')['genotipo'].nunique()
        balance_columnas = book.groupby('columna')['genotipo'].nunique()

        # Preparar resultados
        resultados = {
            'genotipos_por_bloque': None,
            'problemas_genotipos': problemas_genotipos,
            'duplicados_within_block': duplicados_within_block if not duplicados_within_block.empty else None,
            'duplicados_across_blocks': duplicados_across_blocks if not duplicados_across_blocks.empty else None,
            'balance_filas': balance_filas.to_dict(),
            'balance_columnas': balance_columnas.to_dict()
        }

        # Imprimir resultados
        print("=== Verificación del Diseño RCBD ===\n")

        if not problemas_genotipos:
            print("Todos los genotipos aparecen exactamente una vez en cada bloque.\n")
        else:
            print("Problemas encontrados en los bloques:")
            for problema in problemas_genotipos:
                bloque = problema['bloque']
                if 'genotipos_faltantes' in problema:
                    faltantes = problema['genotipos_faltantes']
                    print(f"- Bloque {bloque}: Genotipos faltantes: {faltantes}")
                if 'genotipos_repetidos' in problema:
                    repetidos = problema['genotipos_repetidos']
                    print(f"- Bloque {bloque}: Genotipos repetidos: {repetidos}")
            print()

        if duplicados_within_block.empty:
            print("No se encontraron parcelas duplicadas en la misma fila y columna dentro del mismo bloque.\n")
        else:
            print("Se encontraron parcelas duplicadas en la misma posición dentro del mismo bloque:")
            print(duplicados_within_block[['bloque', 'fila', 'columna', 'genotipo']])
            print()

        if duplicados_across_blocks.empty:
            print("No se encontraron genotipos repetidos en la misma posición a través de diferentes bloques.\n")
        else:
            print("Se encontraron genotipos que aparecen en la misma posición en diferentes bloques:")
            print(duplicados_across_blocks[['bloque', 'fila', 'columna', 'genotipo']].sort_values(['fila', 'columna', 'genotipo', 'bloque']))
            print()

        print("Balance de genotipos por fila:")
        for fila, count in balance_filas.items():
            print(f"- Fila {fila}: {count} genotipos únicos")

        print("\nBalance de genotipos por columna:")
        for columna, count in balance_columnas.items():
            print(f"- Columna {columna}: {count} genotipos únicos")

        print("\n=== Fin de la Verificación ===")

        return resultados

    def mostrar_plan(self, bloque=None):
        """
        Muestra el plan de disposición de genotipos para el bloque especificado.
        Si no se especifica un bloque, muestra los planes para todos los bloques.

        Parámetros:
            bloque (int): Número del bloque a mostrar. Si es None, muestra todos.
        """
        if bloque is not None:
            if bloque in self.plan:
                print(f"Plan del Bloque {bloque}:\n")
                print(self.plan[bloque])
            else:
                print(f"El bloque {bloque} no existe en el diseño.")
        else:
            for blk in sorted(self.plan.keys()):
                print(f"Plan del Bloque {blk}:\n")
                print(self.plan[blk])

def gnc(ng):
    # (La función permanece igual)
    return int(np.ceil(np.sqrt(ng)))

def fp(nr, nc, serpentine):
    # (La función permanece igual)
    plan_id = np.arange(1, nr * nc + 1).reshape(nr, nc, order='F')  # Llenar por columnas
    if serpentine == 'yes':
        for i in range(nr):
            if i % 2 != 0:
                plan_id[i, :] = plan_id[i, ::-1]
    return plan_id

def diseño_rcbd(geno, nb, nc=None, serpentine='yes', alongside='no'):
    # Validar argumentos
    if nb < 2:
        raise ValueError("Debe haber al menos 2 bloques.")
    if len(geno) < 2:
        raise ValueError("Debe haber al menos 2 genotipos.")
    if alongside not in ['no', 'rows', 'columns']:
        raise ValueError("El parámetro 'alongside' debe ser 'no', 'rows' o 'columns'.")
    if serpentine not in ['yes', 'no']:
        raise ValueError("El parámetro 'serpentine' debe ser 'yes' o 'no'.")

    ng = len(geno)  # Número de genotipos

    # Calcular nc si es None
    if nc is None:
        nc = gnc(ng)

    nr = int(np.ceil(ng / nc))  # Número de filas

    # Generar plan_id
    plan_id = fp(nr, nc, serpentine)

    # Crear el plan de campo
    plan = {}  # Usaremos un diccionario para almacenar el plan de cada bloque

    # Crear el libro de campo
    records = []

    for k in range(nb):
        # Asignar genotipos aleatoriamente
        sg = np.random.permutation(geno)
        # Ajustar el tamaño de sg si es necesario
        sg_full = np.full(nr * nc, None, dtype=object)
        sg_full[:len(sg)] = sg
        # Crear la matriz del plan para este bloque
        block_plan = sg_full.reshape(nr, nc, order='F')

        # Si se usa orden serpentino, aplicar la inversión de columnas en filas impares
        if serpentine == 'yes':
            for i in range(nr):
                if i % 2 != 0:
                    block_plan[i, :] = block_plan[i, ::-1]

        # Convertir la matriz a DataFrame para mejor legibilidad
        block_df = pd.DataFrame(
            block_plan,
            index=[f'Fila {i+1}' for i in range(nr)],
            columns=[f'Columna {j+1}' for j in range(nc)]
        )
        # Agregar al diccionario del plan
        plan[k + 1] = block_df

        # Agregar registros al libro de campo
        for i in range(nr):
            for j in range(nc):
                genotype = block_plan[i, j]
                if genotype is not None:
                    plot_number = plan_id[i, j] + ng * k  # Número de parcela
                    fila = i + 1
                    columna = j + 1
                    bloque = k + 1

                    # Ajustar filas y columnas según 'alongside'
                    if alongside == 'rows':
                        columna += k * nc
                    elif alongside == 'columns':
                        fila += k * nr

                    records.append({
                        'Plot': plot_number,
                        'bloque': bloque,
                        'fila': fila,
                        'columna': columna,
                        'genotipo': genotype
                    })

    book = pd.DataFrame(records)

    # Ordenar por número de parcela si serpentine es 'yes'
    if serpentine == 'yes' and nr > 1:
        book = book.sort_values(['Plot']).reset_index(drop=True)
    else:
        book = book.sort_values(['bloque', 'fila', 'columna']).reset_index(drop=True)

    # Reordenar columnas
    book = book[['Plot', 'bloque', 'fila', 'columna', 'genotipo']]

    # Retornar la instancia de FieldLayout con el plan actualizado
    return FieldLayout(book, plan)