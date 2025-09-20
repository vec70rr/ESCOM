import heapq
import time
import os  

# El estado objetivo 
ESTADO_FINAL = ((1, 2, 3, 4),
                (5, 6, 7, 8),
                (9, 10, 11, 12),
                (13, 14, 15, 0)) # 0 representa el espacio vacío

# Mapa precalculado de las posiciones finales de cada ficha para la heurística
POSICIONES_FINALES = {ficha: (fila, col) for fila, fila_vals in enumerate(ESTADO_FINAL) for col, ficha in enumerate(fila_vals)}


def limpiar_pantalla():
    """Limpia la pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_tablero(estado):
    print("-" * 13)
    for fila in estado:
        print("|", " ".join(f"{num:2}" if num != 0 else "  " for num in fila), "|")
    print("-" * 13)

def encontrar_posicion_vacia(estado):
    for i, fila in enumerate(estado):
        if 0 in fila:
            return i, fila.index(0)
    return None

def es_resolvible(estado):
    """Verifica si un estado tiene solución"""
    plano = [num for fila in estado for num in fila if num != 0]
    inversiones = sum(1 for i in range(len(plano)) for j in range(i + 1, len(plano)) if plano[i] > plano[j])
    fila_vacia, _ = encontrar_posicion_vacia(estado)
    fila_vacia_desde_abajo = 4 - fila_vacia
    
    if inversiones % 2 != 0:
        return fila_vacia_desde_abajo % 2 == 0
    else:
        return fila_vacia_desde_abajo % 2 != 0

def obtener_siguientes_estados(estado):
    siguientes = []
    fila_vacia, col_vacia = encontrar_posicion_vacia(estado)
    movimientos = [(-1, 0, 'Arriba'), (1, 0, 'Abajo'), (0, -1, 'Izquierda'), (0, 1, 'Derecha')]
    
    for df, dc, _ in movimientos:
        nueva_fila, nueva_col = fila_vacia + df, col_vacia + dc
        if 0 <= nueva_fila < 4 and 0 <= nueva_col < 4:
            nuevo_estado_lista = [list(fila) for fila in estado]
            ficha_movida = nuevo_estado_lista[nueva_fila][nueva_col]
            nuevo_estado_lista[fila_vacia][col_vacia] = ficha_movida
            nuevo_estado_lista[nueva_fila][nueva_col] = 0
            siguientes.append(tuple(map(tuple, nuevo_estado_lista)))
    return siguientes

# ==========#
# ANIMACIÓN #
# ==========#
def animar_solucion(resultado):
    camino, tiempo, estados_explorados = resultado
    if not camino:
        print("No se encontró una solución.")
        return
    
    print("Solución encontrada")
    print(f"Total de movimientos: {len(camino) - 1}")
    print(f"Estados explorados por A*: {estados_explorados}")
    print(f"Tiempo de cálculo: {tiempo:.5f} segundos.")
    print("\nIniciando animación en 3 segundos...")
    time.sleep(3)

    for i, estado in enumerate(camino):
        limpiar_pantalla()
        print("Resolviendo el 15-Puzzle...")
        print(f"\nPaso {i} / {len(camino) - 1}")
        imprimir_tablero(estado)
        # Pausa entre movimientos
        time.sleep(0.8)
    
    print("\n¡Puzzle resuelto!")

# --------------#
# ALGORITMO A*  #
# --------------#

def heuristica_manhattan(estado):
    distancia_total = 0
    for i in range(4):
        for j in range(4):
            ficha = estado[i][j]
            if ficha != 0:
                fila_final, col_final = POSICIONES_FINALES[ficha]
                distancia_total += abs(i - fila_final) + abs(j - col_final)
    return distancia_total

def reconstruir_camino(camino_previo, estado_actual):
    camino_total = [estado_actual]
    while estado_actual in camino_previo and camino_previo[estado_actual] is not None:
        estado_actual = camino_previo[estado_actual]
        camino_total.append(estado_actual)
    return list(reversed(camino_total))

def resolver_con_a_estrella(estado_inicial):
    inicio_tiempo = time.time()
    frontera = [(heuristica_manhattan(estado_inicial), estado_inicial)]
    camino_previo = {estado_inicial: None}
    costo_g = {estado_inicial: 0}
    estados_explorados = 0

    while frontera:
        _, estado_actual = heapq.heappop(frontera)
        estados_explorados += 1

        if estado_actual == ESTADO_FINAL:
            fin_tiempo = time.time()
            camino = reconstruir_camino(camino_previo, estado_actual)
            return camino, fin_tiempo - inicio_tiempo, estados_explorados

        for siguiente_estado in obtener_siguientes_estados(estado_actual):
            nuevo_costo_g = costo_g[estado_actual] + 1
            if siguiente_estado not in costo_g or nuevo_costo_g < costo_g[siguiente_estado]:
                costo_g[siguiente_estado] = nuevo_costo_g
                costo_h = heuristica_manhattan(siguiente_estado)
                costo_f = nuevo_costo_g + costo_h
                heapq.heappush(frontera, (costo_f, siguiente_estado))
                camino_previo[siguiente_estado] = estado_actual
                
    fin_tiempo = time.time()
    return None, fin_tiempo - inicio_tiempo, estados_explorados

# -----#
# MAIN #
# -----#

if __name__ == "__main__":
    # Estado inicial
    estado_inicial = ((1, 2, 3, 4),
                      (5, 6, 7, 8),
                      (9, 15, 14, 12),
                      (13, 11, 10, 0))

    limpiar_pantalla()
    print("Estado inicial del puzzle:")
    imprimir_tablero(estado_inicial)
    
    if not es_resolvible(estado_inicial):
        print("\nEste puzzle no tiene solución matemática.")
    else:
        print("\nCalculando la solución óptima con A*...")
        resultado_a_estrella = resolver_con_a_estrella(estado_inicial)
        
        animar_solucion(resultado_a_estrella)