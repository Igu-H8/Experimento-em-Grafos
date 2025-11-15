import time
import heapq
from .grafos import distancia_nos, coordenadas_nos 


def dijkstra (g, inicio, fim, peso_chave):
    inicio_tempo = time.perf_counter()
    distancia = {no: float ('inf') for no in g.nodes}
    distancia[inicio] = 0
    rotas = {no: [] for no in g.nodes}
    rotas[inicio] = [inicio]
    distancia_no = [(0, inicio)]
    no_expandido = 0

    while distancia_no:
        d, u = heapq.heappop(distancia_no)

        if d > distancia[u]:
            continue

        no_expandido += 1

        if u == fim:
            break

        for v, data in g.adj[u].items():
            peso_minimo = min(d.get(peso_chave, float('inf')) for d in data.values())
            nova_distancia = distancia[u] + peso_minimo

            if nova_distancia < distancia[v]:
                distancia[v] = nova_distancia
                rotas[v] = rotas[u] + [v]
                heapq.heappush(distancia_no, (nova_distancia, v))

    tempo_tomado = time.perf_counter() - inicio_tempo

    rota = rotas[fim] if distancia[fim] != float('inf') else None
    custo_rota = distancia[fim] 

    return tempo_tomado, custo_rota, no_expandido, rota

def a_estrela(g, inicio, fim, peso_chave): # A*
    inicio_tempo = time.perf_counter()

    peso_g = {no: float('inf') for no in g.nodes}
    peso_g[inicio] = 0

    peso_f = {no: float('inf') for no in g.nodes}
    peso_f [inicio] = distancia_nos(inicio, fim, g)

    rotas = {no: [] for no in g.nodes}
    rotas[inicio] = [inicio]

    distancia_no = [(peso_f[inicio], inicio)]
    no_expandido = 0

    while distancia_no:
        f, u = heapq.heappop(distancia_no)

        if f > peso_f[u]:
            continue

        no_expandido += 1

        if u == fim:
            break

        for v, data in g.adj[u].items():
            peso_minimo = min(d.get(peso_chave, float('inf')) for d in data.values())

            tentativa_peso_g = peso_g[u] + peso_minimo

            if tentativa_peso_g < peso_g[v]:
                peso_g[v] = tentativa_peso_g
                rotas[v] = rotas[u] + [v]

                peso_h = distancia_nos(v, fim, g)
                novo_peso_f = peso_g[v] + peso_h
                peso_f[v] = novo_peso_f
                heapq.heappush(distancia_no, (novo_peso_f, v))
    
    tempo_tomado = time.perf_counter() - inicio_tempo

    rota = rotas[fim] if peso_g[fim] != float('inf') else None
    custo_rota = peso_g[fim]

    return tempo_tomado, custo_rota, no_expandido, rota

def bidirecional(g, inicio, fim, peso_chave, algoritmo='dijkstra'): # dijkstra & A*
    tempo_inicio = time.perf_counter()

    g_score_f = {no: float('inf') for no in g.nodes}
    g_score_b = {no: float('inf') for no in g.nodes}
    g_score_f[inicio] = 0
    g_score_b[fim] = 0 

    f_score_f = {no: float('inf') for no in g.nodes}
    f_score_b = {no: float('inf') for no in g.nodes}

    if algoritmo == 'a_estrela':
        f_score_f[inicio] = distancia_nos(inicio, fim, g)
        f_score_b[fim] = distancia_nos(fim, inicio, g)
        distancia_no_f = [(f_score_f[inicio], inicio)]
        distancia_no_b = [(f_score_b[fim], fim)]

    else:
        distancia_no_f = [(0, inicio)]
        distancia_no_b = [(0, fim)]

    rotas_f = {inicio: [inicio]}
    rotas_b = {fim: [fim]}

    mu = float('inf')
    nos_expandido = 0
    lendo_no = None

    while distancia_no_f and distancia_no_b:
        custo_f = distancia_no_f[0][0]
        custo_b = distancia_no_b[0][0]
        
        if custo_f + custo_b >= mu:
            break

        if custo_f < custo_b:
            _, u = heapq.heappop(distancia_no_f)
            nos_expandido += 1

            for v, data in g.adj[u].items():
                peso_minimo = min(d.get(peso_chave, float('inf')) for d in data.values())
                tentativa_g = g_score_f[u] + peso_minimo

                if tentativa_g < g_score_f[v]:
                    g_score_f[v] = tentativa_g
                    rotas_f[v] = rotas_f[u] + [v] 

                    if algoritmo == 'a_estrela':
                        f_score_f[v] = g_score_f[v] + distancia_nos(v, fim, g)
                        heapq.heappush(distancia_no_f, (f_score_f[v], v))
                    
                    else:
                        heapq.heappush(distancia_no_f, (g_score_f[v], v)) 
                        
                    if v in g_score_b:
                        novo_mu = g_score_f[v] + g_score_b[v]
                        
                        if novo_mu < mu:
                            mu = novo_mu
                            lendo_no = v

        else: 
            _, u = heapq.heappop(distancia_no_b)
            nos_expandido += 1

            for v, data in g.pred[u].items():
                peso_minimo = min(d.get(peso_chave, float('inf')) for d in data.values())
                tentativa_g = g_score_b[u] + peso_minimo

                if tentativa_g < g_score_b[v]:
                    g_score_b[v] = tentativa_g
                    rotas_b[v] = [v] + rotas_b[u]

                    if algoritmo == 'a_estrela':
                        f_score_b[v] = g_score_b[v] + distancia_nos(v, inicio, g)
                        heapq.heappush(distancia_no_b, (f_score_b[v], v))
                    
                    else:
                        heapq.heappush(distancia_no_b, (g_score_b[v], v)) 

                    if v in g_score_f:
                        novo_mu =  g_score_f[v] + g_score_b[v]

                        if novo_mu < mu:
                            mu = novo_mu
                            lendo_no = v

    tempo_tomado = time.perf_counter() - tempo_inicio
    custo_rota = mu

    if lendo_no:
        rota = rotas_f[lendo_no] + rotas_b[lendo_no][1:]

    else:
        rota = None

    return tempo_tomado, custo_rota, nos_expandido, rota
