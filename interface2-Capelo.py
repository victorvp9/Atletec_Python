import matplotlib.pyplot as plt
import math
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
import tkinter as tk
from tkinter import simpledialog, messagebox
import sys
import os
from decimal import Decimal

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o arquivo, funcionando tanto para modo desenvolvimento quanto para executável PyInstaller """
    # Verifica se está rodando em um executável PyInstaller
    if getattr(sys, 'frozen', False):
        # Caminho quando está rodando como executável PyInstaller
        base_path = os.path.dirname(sys.executable)
    else:
        # Caminho quando está rodando no ambiente de desenvolvimento
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Variáveis globais para armazenar os pontos e outros parâmetros
fig, ax = plt.subplots()
x_coords = []
y_coords = []
coordenadas = []
xmin, xmax, ymin, ymax = 0, 0, 0, 0
bottom_point = None
bigger_side_point = None
short_side = 0
retangulo_rotacionado = None
campo_img = plt.imread(resource_path('campo_futebol.jpg'))
margem = 0.00005
right = 1
def dist_euclidiana(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_lados(campo):
    global coordenadas, bigger_side_point, bottom_point, xmin, xmax, ymin, ymax, retangulo_rotacionado, right, short_side
    coordenadas = campo
    menor_latitude = min(campo, key=lambda x: x[0])
    bottom_point_index = campo.index(menor_latitude)
    bottom_point = (coordenadas[bottom_point_index][0], coordenadas[bottom_point_index][1])
    next_point = (coordenadas[(bottom_point_index+1)%4][0], coordenadas[(bottom_point_index+1)%4][1])
    prev_point = (coordenadas[(bottom_point_index+3)%4][0], coordenadas[(bottom_point_index+3)%4][1])
    
    next_hip = dist_euclidiana(next_point, bottom_point)
    prev_hip = dist_euclidiana(prev_point, bottom_point)

    if prev_hip > next_hip:
        bigger_side_point = prev_point
        xmin, xmax, ymin, ymax = - margem, prev_hip+margem, - margem, next_hip+margem
        short_side = dist_euclidiana(next_point, bottom_point)
    else:
        bigger_side_point = next_point
        xmin, xmax, ymin, ymax = - margem, next_hip+margem, - margem, prev_hip+margem
        short_side = dist_euclidiana(prev_point, bottom_point)

    retangulo_rotacionado = [
        [xmin, ymin],
        [xmax, ymin],
        [xmax, ymax],
        [xmin, ymax]
    ]
    retangulo_rotacionado = Polygon(retangulo_rotacionado)

    if bigger_side_point[1] > bottom_point[1]:
        right = 1
    else:
        right = -1


def calculate_alpha(new_p):
    global bottom_point, bigger_side_point
    a = dist_euclidiana(bottom_point, new_p)
    b = dist_euclidiana(bottom_point, bigger_side_point)
    c = dist_euclidiana(new_p, bigger_side_point)

    cos_C = (a**2 + b**2 - c**2) / (2 * a * b)
    angulo_C = math.acos(cos_C)
    return angulo_C

def transform_point(point):
    global bottom_point, bigger_side_point, short_side, right

    alpha = calculate_alpha(point)
    hip = dist_euclidiana(bottom_point, point)
    new_long = hip * np.cos(alpha)
    new_lat = hip * np.sin(alpha)
    if right == -1:
        new_lat = short_side - new_lat
    return new_long, new_lat

def new_point(lat, long):
    global x_coords, y_coords, margem, coordenadas

    lat, long = transform_point((lat, long))
    x_coords.append(lat)
    y_coords.append(long)
    # atualizar_heatmap()  # Atualiza o heatmap após adicionar o ponto

def random_points(qnt_pontos):
    global x_coords, y_coords, xmin, xmax, ymin, ymax, margem
    x_coords = []
    y_coords = []
    for _ in range(qnt_pontos):
        while True:
            lat = np.random.uniform(xmin + margem, xmax - margem)
            long = np.random.uniform(ymin + margem, ymax - margem)
            x_coords.append(lat)
            y_coords.append(long)
            break

def atualizar_heatmap():
    global x_coords, y_coords, xmin, xmax, ymin, ymax, campo_img, retangulo_rotacionado, margem, bottom_point

    points = np.array([x_coords, y_coords]).T

    if len(points) == 0:
        print("No points to plot.")
        return
    
    heatmap, xedges, yedges = np.histogram2d(points[:, 0], points[:, 1], bins=60, range=[[xmin, xmax], [ymin, ymax]])
    heatmap = gaussian_filter(heatmap, sigma=2)
    
    cmap = LinearSegmentedColormap.from_list('transparente_vermelho', [(0,0,0,0),'green', 'yellow', 'red'])  
    
    ax.clear()  # Limpa o conteúdo do eixo
    ax.imshow(campo_img, extent=[xmin, xmax, ymin, ymax], origin='lower', aspect='auto')
    ax.imshow(heatmap.T, extent=[xmin, xmax, ymin, ymax], origin='lower', cmap=cmap, alpha=0.6)
    ax.plot(x_coords[len(x_coords)-1], y_coords[len(y_coords)-1], 'bo')  # Ponto azul


    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.set_xlabel('Longitude')
    # ax.set_ylabel('Latitude')
    # ax.set_title('Mapa de Calor do Jogador sobre o Campo de Futebol')
    ax.set_aspect('equal')
    fig.patch.set_alpha(0)
    # plt.plot()
    fig.canvas.draw()  # Redesenha a figura
    try:
        plt.savefig("C:/Users/victo/Documents/Projetos/Atletec/Atletec/lib/images/heatmap.png")
        print("Heatmap atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar heatmap: {e}")

def main():
    global campo_img, coordenadas
    ## LESC
    coordenadas = [
        (-3.7450360086986754, -38.577945173176495),
        (-3.7445026060122393, -38.57812786542045),
        (-3.7442280272874515, -38.57730236713294),
        (-3.744759179496814, -38.57711741942873)
    ]
    ## CAMP NOU
    # coordenadas = [
    #     (41.38122406820053, 2.1222125083605134),
    #     (41.38144817870427, 2.1229640987797285),
    #     (41.380573369840775, 2.123433752893428),
    #     (41.38034567473057, 2.122682696100784)
    # ]

    ## CASTELÃO
    # coordenadas = [
    #     (-3.8077474061148386, -38.52218218490945),
    #     (-3.806807293860556, -38.52209549842854),
    #     (-3.8067584515492863, -38.52270503041305),
    #     (-3.807691763418932, -38.522787089208705)
    # ]

    ## PRESIDENTE VARGAS:
    # coordenadas = [
    #     (-3.7464570344603114, -38.53697144194994),
    #     (-3.7462691952309846, -38.536366817230395),
    #     (-3.745340457015739, -38.536655825233346),
    #     (-3.745495124743257, -38.537272071595254)
    # ]

    ## IEFES: 
    # coordenadas = [
    #     (-3.7527205525705765, -38.57344429223954),
    #     (-3.7524305497299832, -38.57291373093974),
    #     (-3.7516279832274417, -38.573354738899134),
    #     (-3.751889323240939, -38.57386671365659)
    # ]

    calculate_lados(coordenadas)

# lock_file = "C:/Users/rafae/Projects/atletec/file.lock"
# data_file = "C:/Users/rafae/Projects/atletec/coordinates.txt"

# def read_from_file():
#     while os.path.exists(lock_file):
#         time.sleep(0.1)
#     try:
#         if(not os.path.exists(lock_file)):
#             open(lock_file, 'w').close()
#         with open(data_file, 'r') as file:
#             return file.read().split()
#     finally:
#         if(os.path.exists(lock_file)):
#             os.remove(lock_file)

main()
# plt.ion()  # Modo interativo do Matplotlib
x_coords.clear()
y_coords.clear()
atualizar_heatmap()
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_function():
    data = request.get_json()
    data = data['data'].split()
    print(data)
    new_point(float(data[1]), float(data[2]))
    print(float(data[1]), float(data[2]))
    if data[0] == 'Heat':
        atualizar_heatmap()
    res = {'message':'Função executada!'}
    return jsonify(res)

@app.route('/atualizar_coordenadas', methods = ['POST'])
def atualizar_coordenadas():
    global coordenadas

    data = request.get_json()
    
    novas_coordenadas_str = data.get('coordenadas')
    print("\n Novas coordenadas = ", novas_coordenadas_str, "\n")
    coordenadas_lista = list(map(float, novas_coordenadas_str.split(', ')))
    novas_coordenadas = [(coordenadas_lista[i], coordenadas_lista[i+1]) for i in range(0, len(coordenadas_lista), 2)]
    print("\n",novas_coordenadas)
    coordenadas = novas_coordenadas

    calculate_lados(coordenadas)

    return jsonify({'status': 'Coordenadas Atualizadas com sucesso', 'coordenadas': coordenadas})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
# async def server(websocket, path):
#     async for message in websocket:
#         print(message)
#         await websocket.send('ACK')

# start_server = websockets.serve(server, 'localhost', 65432)

# asyncio.get_event_loop().run_until_complete(start_server)
# print('Servidor WebSocket ouvindo em ws://localhost:65432')
# asyncio.get_event_loop().run_forever()

# last = 0
# while True:
#     data = read_from_file()
#     if last == int(data[1]):
#         continue
#     new_point(float(data[2]), float(data[3]))
#     print(data)
#     last = int(data[1])
#     if data[0] == 'Heat':
#         atualizar_heatmap()
#         print(len(x_coords)) 