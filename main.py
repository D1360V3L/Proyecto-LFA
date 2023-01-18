# -*- coding: utf-8 -*-
# LENGUAGES FORMALES Y AUTOMATAS
# FACULTAD DE INGENIERÍA, UNAM, 2023-1
#
#
import graphviz as gv # Librería para llevar a cabo la impresión del automata en archivo PNG

import random # Librería generadora de números aleatorios, usada para generar colores aleatorios
              # en el automata en PNG

from collections import deque # Librerías diversas para la generación de la ruta más corta
import requests
import math
import sys
import json
import csv




def breadth_first_search(start, goal, stations, adjacency):
    #
    # TODO:
    #
    # Implementación del algoritmo Breadth-First-Search para encontrar una ruta
    # desde el punto (start_lat, start_lon) hasta el punto (goal_lat, goal_lon).
    # Devuelve la ruta como una lista de los nombres de las estaciones a recorrer.
    # Considerar:
    # 'start' es el nombre de la estación de inicio
    # 'goal' es el nombre de la estación de destino
    # 'stations' es una lista de todos los nombres de las estaciones: ['Zocalo', 'Allende', 'Bellas Artes' ... ]
    # 'adjacency' es un diccionario donde las claves son los nombres de las estaciones y cada
    # valor es una lista de las estaciones con las que está conectada la tecla. Ejemplo:
    # { 'Zócalo' :[ 'Allende' 'Pino Suárez']
    # 'Chabacano':[ 'Viaducto', 'San Antonio Abad', 'Obrera', 'La Viga', 'Jamaica', 'Lazarón Cárdenas'] }
    #
    open_list   = deque()
    closed_list = []
    g_values = {}
    previous = {}
    for n in stations:
        g_values[n] = 99999
        previous[n] = None
    path = []
    open_list.append(start)
    g_values[start] = 0
    current = None
    while current!= goal and len(open_list) > 0:
        current = open_list.popleft()
        closed_list.append(current)
        for n in adjacency[current]:
            if n in closed_list:
                continue
            g = g_values[current] + 1
            if g < g_values[n]:
                g_values[n] = g
                previous[n] = current
            if (n not in open_list) and (n not in closed_list):
                open_list.append(n)
    while current != None:
        path.insert(0, current)
        current = previous[current]
    return path


def get_subway_stations():
    #
    # Esta función devuelve una lista de tuplas de la forma [[lat, lon, nombre], [lat, lon, nombre], ...]
    # que contiene los datos de todas las estaciones del metro de la Ciudad de México.
    #
    #url="https://datos.cdmx.gob.mx/api/records/1.0/search/?dataset=estaciones-metro&rows=200"
    #
    json_response = open("SubwayStations.json",'r').read()
    json_response = json.loads(json_response)
    stations = []
    for record in json_response['features']:
        lat  = record['geometry']['coordinates'][1]
        lon  = record['geometry']['coordinates'][0]
        name = record['properties']['stop_name']
        try:
            name = name[0:name.index("_")]
        except:
            pass
        stations.append([lat, lon, name])
    return stations

def get_subway_lines():
    #
    # Esta función devuelve una lista de la forma:
    # [ [[lat,lon],[lat,lon],...,[lat,lon]], [[lat,lon],[lat,lon],...,[lat,lon]], ... , [[lat,lon],[lat,lon],...,[lat,lon]] ]
    # ------------------------------------- ------------ ------------------------ -------------------------- ---------
    # Estaciones de la línea 0 Estaciones de la línea 1 Estaciones de la línea N-1
    # La API de líneas de metro de CdMx solo devuelve las coordenadas de cada estación, pero no el nombre.
    # Por lo tanto, es necesario asociar cada geopunto con su nombre correspondiente
    # Usando la función find_neares_station
    #
    #url="https://datos.cdmx.gob.mx/api/records/1.0/search/?dataset=lineas-de-metro&rows=12"
    #json_response = requests.get(url).json()
    #
    stations_csv = open("SubwayLines.csv",'r')
    csv_reader = csv.reader(stations_csv, delimiter=',')
    line_jsons = []
    for row in csv_reader:
        if row[2][0] != "{":
            continue
        line_jsons.append(json.loads(row[2]))
    lines = []
    for l in line_jsons:
        line_stations = []
        for p in l['coordinates']:
            line_stations.append(p)
        lines.append(line_stations)
    return lines

def build_adjacency(lines, stations):
    #
    # Esta función devuelve un diccionario donde las claves son los nombres de las estaciones y cada
    # valor es una lista de las estaciones con las que está conectada la tecla. Ejemplo:
    # { 'Zócalo' :[ 'Allende' 'Pino Suárez']
    # 'Chabacano':[ 'Viaducto', 'San Antonio Abad', 'Obrera', 'La Viga', 'Jamaica', 'Lazarón Cárdenas'] }
    # El diccionario resultante representa la matriz de adyacencia del Gráfico Subterráneo de CdMx
    #
    A = {}
    for lat,lon,name in stations:
        A[name] = [] 
    for line in lines:
        next = find_nearest_station(line[1][1], line[1][0], stations)
        name = find_nearest_station(line[0][1], line[0][0], stations)
        A[name].append(next)
        for i in range(1, len(line)-1):
            prev = find_nearest_station(line[i-1][1], line[i-1][0], stations)
            next = find_nearest_station(line[i+1][1], line[i+1][0], stations)
            name = find_nearest_station(line[i  ][1], line[i  ][0], stations)
            A[name].append(prev)
            A[name].append(next)
        prev = find_nearest_station(line[len(line)-2][1], line[len(line)-2][0], stations)
        name = find_nearest_station(line[len(line)-1][1], line[len(line)-1][0], stations)
        A[name].append(prev)
    return A

def find_nearest_station(current_lat, current_lon, stations):
    #
    # Esta función devuelve el nombre de la estación más cercana al
    # punto [lat_actual, longitud_actual], dada una lista de estaciones de la forma
    # [[lat, lon, nombre], [lat, lon, nombre], ...]
    #
    min_d = sys.maxsize
    nearest_station = None
    for [lat, lon, name] in stations:
        d = math.sqrt((current_lon - lon)**2 + (current_lat - lat)**2)
        if d < min_d:
            min_d = d
            nearest_station = name
    return nearest_station

def random_color():
    #
    # Esta función generará un color aleatorio en formato HEX,
    # donde el color se representa como una cadena en el formato "#RRGGBB".
    #
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    return hex_color



def main(start, goal):
    stations  = get_subway_stations()
    lines     = get_subway_lines()
    adjacency = build_adjacency(lines, stations)
    path      = breadth_first_search(start, goal, [name for [lat, lon, name] in stations], adjacency)
    print("La mejor ruta es:")
    #path[0]=''
    print(' -> '.join(map(str, path)))
    automaton = gv.Graph(format='png')
    color = random_color()
    for p in range(len(path)-1):
        color = random_color()
        automaton.node(path[int(p)], color=str(color), penwidth='3')
        automaton.edge(path[int(p)], path[int(p+1)], label='1', color = str(color), penwidth='3')

    color = random_color()
    automaton.node(path[int(len(path)-1)], color=str(color), penwidth='3')

    automaton.render('automaton')
    print("\n \n \n")
    print("Archivo PNG del automata creado en la carpeta\n \n \n")



if __name__ == '__main__':
    start = None
    goal  = None
    start_lat = None
    start_lon = None
    goal_lat  = None
    goal_lon  = None
    stations  = get_subway_stations()
    names     = [name for [lat, lon, name] in stations]

    if '--start' in sys.argv:
        start = sys.argv[sys.argv.index('--start')+1]

    if '--goal' in sys.argv:
        goal = sys.argv[sys.argv.index('--goal')+1]
    
    if '--start_lat' in sys.argv:
        start_lat = float(sys.argv[sys.argv.index('--start_lat')+1])
    if '--start_lon' in sys.argv:
        start_lon = float(sys.argv[sys.argv.index('--start_lon')+1])
    if '--goal_lat' in sys.argv:
        goal_lat = float(sys.argv[sys.argv.index('--goal_lat')+1])
    if '--goal_lon' in sys.argv:
        goal_lon = float(sys.argv[sys.argv.index('--goal_lon')+1])
    
    if start_lat != None and start_lon != None:
        start = find_nearest_station(start_lat, start_lon, stations)
    if goal_lat != None and goal_lon != None:
        goal  = find_nearest_station(goal_lat,  goal_lon , stations)
    
    if start == None:
        start = input('Ingresa la estación de origen:  ')
    if goal  == None:
        goal  = input('Ingresa la estación de destino: ')

    if start not in names:
        print("Estación de origen invalida")
        exit()
    if goal not in names:
        print("Estación de destino invalida")
        exit()


    main(start, goal)
