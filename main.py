import pandas
import random
import time
import os
import numpy
import subprocess
import platform
import matplotlib.pyplot as plt
from recursos.grafos import grafo, plotar_grafo 
from recursos.algoritmos import dijkstra, a_estrela, bidirecional

OUTPUT_DIR = 'dados'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def origem_destino(g, pares=100):
    nos = list(g.nodes)
    recursos = random.choices(nos, k=pares)
    destinos = random.choices(nos, k=pares)
    return[(s, t) for s, t in zip(recursos, destinos) if s != t]

def executar_experimento(g, interacoes=100):
    print(f"Executando o experimento com {interacoes} interações...")
    pares = origem_destino(g, interacoes)
    resultados= []

    pesos_teste = ['travel_time', 'length', 'risk']

    for i, (recursos, destinos) in enumerate(pares):
        print(f"Executando par {i+1}/{len(pares)}...")

        for weight in pesos_teste:
            t_d_uni, cost_d_uni, expanded_d_uni, _ = dijkstra(g, recursos, 
            destinos, weight)
            
            t_d_bi, cost_d_bi, expanded_d_bi, _ = bidirecional(
                g, recursos, destinos, weight, algoritmo='dijkstra')

            t_a_uni, cost_a_uni, expanded_a_uni, _ = a_estrela(
                g, recursos, destinos, weight)

            t_a_bi, cost_a_bi, expanded_a_bi, _ = bidirecional(
                g, recursos, destinos, weight, algoritmo='a_estrela')
            
            resultados.append({
                'par_id': i, 'weight_type': weight, 's_node': recursos, 't_node': destinos,
                'd_uni_time': t_d_uni, 'd_uni_cost': cost_d_uni, 'd_uni_nodes': expanded_d_uni,
                'd_bi_time': t_d_bi, 'd_bi_cost': cost_d_bi, 'd_bi_nodes': expanded_d_bi,
                'a_uni_time': t_a_uni, 'a_uni_cost': cost_a_uni, 'a_uni_nodes': expanded_a_uni,
                'a_bi_time': t_a_bi, 'a_bi_cost': cost_a_bi, 'a_bi_nodes': expanded_a_bi,
            })
    return pandas.DataFrame(resultados)

def gerar_e_salvar_grafico_complexidade(csv_path, grafico_path):
    print("\n--- Gerando e salvando gráfico de complexidade... ---")
    
    df = pandas.read_csv(csv_path)
    df_valid = df[df['d_uni_cost'] != numpy.inf]

    df_time = df_valid[df_valid['weight_type'] == 'travel_time']
    mean_values = df_time.mean(numeric_only=True) 

    nodes_data = {
        'Algoritmo': ['Dijkstra Unidirecional', 'Dijkstra Bidirecional', 'A* Unidirecional', 'A* Bidirecional'],
        'Nós Expandidos (Média)': [
            mean_values['d_uni_nodes'],
            mean_values['d_bi_nodes'],
            mean_values['a_uni_nodes'],
            mean_values['a_bi_nodes']
        ]
    }
    df_chart = pandas.DataFrame(nodes_data)

    plt.figure(figsize=(10, 6))
    colors = ['skyblue', 'navy', 'lightcoral', 'darkred']
    plt.bar(df_chart['Algoritmo'], df_chart['Nós Expandidos (Média)'], color=colors)

    plt.title('Nós Expandidos Médios (Custo: Tempo) – Uni vs. Bidirecional')
    plt.ylabel('Número de Nós Expandidos')
    plt.xticks(rotation=15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig(grafico_path)
    print(f"Gráfico de complexidade salvo em {grafico_path}")
    plt.close()


if __name__ == '__main__':
    g = grafo()
    
    if g:
        mapa_path = plotar_grafo(g) 
        df_results = executar_experimento(g, interacoes=100)

        df_results['d_speedup'] = df_results['d_uni_time'] / df_results['d_bi_time']
        df_results['a_speedup'] = df_results['a_uni_time'] / df_results['a_bi_time']
        df_results = df_results[df_results['d_uni_cost'] != numpy.inf]
        
        summary = df_results.groupby('weight_type').agg({
            'd_uni_time': 'mean', 'd_bi_time': 'mean', 'd_speedup': 'mean',
            'd_uni_nodes': 'mean', 'd_bi_nodes': 'mean', 'a_uni_time': 'mean',
            'a_bi_time': 'mean', 'a_speedup': 'mean', 'a_uni_nodes': 'mean',
            'a_bi_nodes': 'mean',
        }).reset_index()
        
        print("\n--- Resultados Agregados (Médias) ---")
        print(summary.to_string())
        
        csv_file_path = os.path.join(OUTPUT_DIR, 'experiment_results_detailed.csv')
        df_results.to_csv(csv_file_path, index=False)
        print(f"\nResultados detalhados salvos em {csv_file_path}")
        
        grafico_file_path = os.path.join(OUTPUT_DIR, 'complexidade_media.png')
        gerar_e_salvar_grafico_complexidade(csv_file_path, grafico_file_path)
        