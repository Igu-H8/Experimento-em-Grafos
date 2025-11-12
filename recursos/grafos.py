import osmnx 
import numpy
import sys

sys. setrecursionlimit(2000)

def grafo(place_name="Recife, Pernambuco, Brazil"):
    try:
        print(f"Buscando malha viária de {place_name}...")

        g = osmnx.graph_from_place(place_name, network_type="drive")
        g = osmnx.project_graph(g)

    except Exception as e:
        print(f"Grafo não encontrado! {e}")
        return None
    
    g = osmnx.add_edge_travel_times(g)

    for u, v, k, data in g.edges(keys=True, data=True):
        fator_risco = numpy.random.uniform(0.1, 0.5)
        data['risk'] = data['lenght'] * fator_risco

    print("pesos 'lenght', 'travel_time' e 'risk' adicionados.")
    return g

def coordenadas_nos(g, u):
    return (g.nodes[u]['x'], g.nodes[u]['y'])

def distancia_nos(u, v, g):
    coordenada_u = coordenadas_nos(g, u)
    coordenada_v = coordenadas_nos(g, v)
    return numpy.sqrt((coordenada_u[0] - coordenada_v[0]) ** 2 + 
                      (coordenada_u[1] - coordenada_v[1]) ** 2)
