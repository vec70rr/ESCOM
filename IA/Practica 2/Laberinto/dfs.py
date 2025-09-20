from colorama import Fore, Style, init
import collections
import copy
import heapq  #? heapq para la cola de prioridad de A*

# Inicializar colorama para los colores
init(autoreset=True)

# --------------------------------------------------------------------------
# SECCIÓN COMÚN Y DE IMPRESIÓN
# --------------------------------------------------------------------------

def imprimir_laberinto(laberinto):
    """
    Imprime el laberinto con colores para una mejor visualización.
    """
    for fila in laberinto:
        linea_a_imprimir = []
        for celda in fila:
            if celda == '*':
                linea_a_imprimir.append(Fore.GREEN + Style.BRIGHT + celda)
            elif celda in ('#', 'I', 'F'):
                linea_a_imprimir.append(Fore.WHITE + Style.BRIGHT + celda)
            else:
                linea_a_imprimir.append(celda)
        print(" ".join(linea_a_imprimir))
    print("\n")

def encontrar_puntos(laberinto):
    """
    Encuentra las coordenadas de los puntos de inicio ('I') y fin ('F').
    """
    inicio, fin = None, None
    for i, fila in enumerate(laberinto):
        if 'I' in fila:
            inicio = (i, fila.index('I'))
        if 'F' in fila:
            fin = (i, fila.index('F'))
    return inicio, fin

# --------------------------------------------------------------------------
# ALGORITMO DE BÚSQUEDA EN PROFUNDIDAD (DFS)
# --------------------------------------------------------------------------

def resolver_con_dfs(laberinto):
    inicio, _ = encontrar_puntos(laberinto)
    if not inicio:
        print("Error: No se encontró 'I'.")
        return

    visitados = set()
    if buscar_solucion_dfs_recursivo(laberinto, inicio[0], inicio[1], visitados):
        laberinto[inicio[0]][inicio[1]] = 'I'
        imprimir_laberinto(laberinto)
    else:
        print("No se pudo encontrar una solución con DFS.\n")

def buscar_solucion_dfs_recursivo(laberinto, fila, columna, visitados):
    if not (0 <= fila < len(laberinto) and 0 <= columna < len(laberinto[0])): ##! La ubicacion esta fuera del mapa
        return False
    if laberinto[fila][columna] == '#' or (fila, columna) in visitados: ##! La ubicacion es un muro o ya se visitó
        return False
    if laberinto[fila][columna] == 'F': ##* La ubicacion es el final del laberinto
        return True

    ## Celda vacia, se agrega a lista de visitados y se marca en el laberinto
    visitados.add((fila, columna))
    if laberinto[fila][columna] != 'I':
        laberinto[fila][columna] = '*'

    ##D, Ab, I, Ar
    if (buscar_solucion_dfs_recursivo(laberinto, fila, columna + 1, visitados) or
        buscar_solucion_dfs_recursivo(laberinto, fila + 1, columna, visitados) or
        buscar_solucion_dfs_recursivo(laberinto, fila, columna - 1, visitados) or
        buscar_solucion_dfs_recursivo(laberinto, fila - 1, columna, visitados)):
        return True
    
    ##! Se llega a un callejon sin salida y se borra el * marcado
    if laberinto[fila][columna] != 'I':
        laberinto[fila][columna] = ' '
    return False

# --------------------------------------------------------------------------
# ALGORITMO DE BÚSQUEDA EN ANCHURA (BFS)
# --------------------------------------------------------------------------

def resolver_con_bfs(laberinto):
    inicio, _ = encontrar_puntos(laberinto)
    if not inicio:
        print("Error: No se encontró 'I'.")
        return

    cola = collections.deque([[inicio]]) ## Cola de caminos
    visitados = {inicio}
    path_solucion = None

    while cola:
        camino_actual = cola.popleft()
        fila, columna = camino_actual[-1]

        if laberinto[fila][columna] == 'F':
            path_solucion = camino_actual
            break

        for df, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]: # Derecha, Abajo, Izquierda, Arriba
            nueva_fila, nueva_columna = fila + df, columna + dc
            vecino = (nueva_fila, nueva_columna) # Vecino a explorar

            if (0 <= nueva_fila < len(laberinto) and 0 <= nueva_columna < len(laberinto[0]) and
                laberinto[nueva_fila][nueva_columna] != '#' and vecino not in visitados): # Verifica que el vecino sea válido
                visitados.add(vecino)
                nuevo_camino = list(camino_actual)
                nuevo_camino.append(vecino)
                cola.append(nuevo_camino)

    if path_solucion:
        for fila, columna in path_solucion:
            if laberinto[fila][columna] not in ('I', 'F'):
                laberinto[fila][columna] = '*'
        imprimir_laberinto(laberinto)
    else:
        print("No se pudo encontrar una solución con BFS.\n")

# --------------------------------------------------------------------------
# ALGORITMO DE BÚSQUEDA INFORMADA A* (A-Estrella)
# --------------------------------------------------------------------------

def distancia_manhattan(punto1, punto2):
    """
    Calcula la distancia de Manhattan, nuestra función heurística h(n).
    """
    return abs(punto1[0] - punto2[0]) + abs(punto1[1] - punto2[1])

def resolver_con_a_estrella(laberinto):
    """
    Prepara y ejecuta la solución usando el algoritmo A*.
    """
    inicio, fin = encontrar_puntos(laberinto)
    if not inicio or not fin:
        print("Error: No se encontró 'I' o 'F'.")
        return
    
    # La cola de prioridad almacenará tuplas: (costo_f, costo_g, camino)
    frontera = [(0, 0, [inicio])] # f=0, g=0, camino=[(inicio)]
    visitados = set()
    path_solucion = None

    while frontera:
        # Sacamos el camino con el menor costo f(n) de la cola de prioridad
        _, costo_g, camino_actual = heapq.heappop(frontera)
        
        posicion_actual = camino_actual[-1]

        if posicion_actual in visitados:
            continue
        
        visitados.add(posicion_actual)

        if posicion_actual == fin:
            path_solucion = camino_actual
            break

        # Explorar vecinos
        for df, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            vecino = (posicion_actual[0] + df, posicion_actual[1] + dc)
            
            if (0 <= vecino[0] < len(laberinto) and 0 <= vecino[1] < len(laberinto[0]) and
                laberinto[vecino[0]][vecino[1]] != '#' and vecino not in visitados):
                
                nuevo_costo_g = costo_g + 1
                heuristico_h = distancia_manhattan(vecino, fin)
                costo_f = nuevo_costo_g + heuristico_h
                
                nuevo_camino = list(camino_actual)
                nuevo_camino.append(vecino)
                
                heapq.heappush(frontera, (costo_f, nuevo_costo_g, nuevo_camino))
    
    if path_solucion:
        for fila, columna in path_solucion:
            if laberinto[fila][columna] not in ('I', 'F'):
                laberinto[fila][columna] = '*'
        imprimir_laberinto(laberinto)
    else:
        print("No se pudo encontrar una solución con A*.\n")

# --------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# --------------------------------------------------------------------------

if __name__ == "__main__":
    laberinto_base = [
        ['I', ' ', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['#', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', '#', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', '#', ' ', '#', '#', '#', '#', ' ', '#'],
        ['#', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', '#'],
        ['#', '#', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#', ' ', '#', ' ', '#', '#', '#', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', '#', '#', '#', '#', '#', ' ', '#', '#', '#', '#', '#', '#', '#', '#', '#', ' ', '#', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', '#', '#', '#', ' ', '#', ' ', '#', ' ', '#', '#', '#', '#', '#', '#', '#', '#', ' ', '#'],
        ['#', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', '#'],
        ['#', ' ', '#', ' ', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', ' ', '#', ' ', '#', '#'],
        ['#', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#', ' ', ' ', '#'],
        ['#', ' ', '#', '#', '#', '#', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#', '#', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#', ' ', ' ', '#'],
        ['#', '#', '#', '#', '#', ' ', '#', '#', '#', '#', '#', ' ', '#', '#', '#', '#', '#', ' ', '#', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', '#'],
        ['#', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#', '#'],
        ['#', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', '#', ' ', '#', '#', '#', '#', '#', '#', '#', ' ', '#', ' ', '#', '#', '#', '#', ' ', 'F'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
    ]

    print(Fore.CYAN + Style.BRIGHT + "--- Laberinto inicial --- \n")

    imprimir_laberinto(laberinto_base)

    # --- Ejecución de DFS ---
    print(Fore.YELLOW + Style.BRIGHT + "1. Solución con Búsqueda en Profundidad (DFS):")
    laberinto_dfs = copy.deepcopy(laberinto_base)
    resolver_con_dfs(laberinto_dfs)
    
    # --- Ejecución de BFS ---
    print(Fore.YELLOW + Style.BRIGHT + "2. Solución con Búsqueda en Anchura (BFS):")
    laberinto_bfs = copy.deepcopy(laberinto_base)
    resolver_con_bfs(laberinto_bfs)
    
    # --- Ejecución de A* ---
    print(Fore.YELLOW + Style.BRIGHT + "3. Solución con Búsqueda Informada (A*):")
    laberinto_a_estrella = copy.deepcopy(laberinto_base)
    resolver_con_a_estrella(laberinto_a_estrella)