"""
Author      : DESMET Aline 
Matricule   : 000474868 (MA2-INFO)
Description : Generate random layouts
"""

import random
import os
from typing import List, Tuple
import copy

Grid = List[List[bool]]
Position = Tuple[int, int]


def createLayout(number_of_layouts: int, height: int, width: int, number_of_clients: int, fuel_level:int, probability: float = 0.9, simplified: bool = False, directory_layout: str = "layouts") -> None:
    try:
        os.mkdir(directory_layout)
    except OSError as error:
        print("{0} was not created as it already exists.".format(directory_layout))
    filename = directory_layout+os.sep+'_'+str(height)+'x'+str(width)+'_'
    for i in range(number_of_layouts):
        file = open(filename+str(i)+".lay", "w+")
        walls = setWallsPositions(height, width, probability)
        clients, fuel_station, airport, taxi_position = setOtherPositions(
            walls, number_of_clients, simplified)

        grid_str = f"{height} {width} {number_of_clients} {fuel_level}\n"
        grid_str += transformToStr(walls, clients,
                                   fuel_station, airport, taxi_position)
        print(grid_str, file=file)
        file.close()


def setWallsPositions(height: int, width: int, probability: float = 0.9) -> Grid:

    city_grid = []
    for i in range(height):  # Lines
        row = []
        for j in range(width):  # Columns
            random_probability = random.random()
            (is_upperLower_borders) = i == 0 or i == height-1
            is_side_borders = j == 0 or j == width-1
            if (is_upperLower_borders) or (is_side_borders):
                row.append(True)
            elif random_probability > probability:
                row.append(True)
            else:
                row.append(False)
        city_grid.append(row)
    return city_grid


def setOtherPositions(walls: Grid, number_of_clients, simplified: bool = False):
    height, width = len(walls), len(walls[0])
    fuel_station = [[False for j in range(width)] for i in range(height)]
    airport = [[False for j in range(width)] for i in range(height)]
    taxi = [[False for j in range(width)] for i in range(height)]
    clients_start = [[False for j in range(width)] for i in range(height)]
    clients_destination = [[False for j in range(width)] for i in range(height)]

    clients_start = setSeveralPositions(
        walls, height, width, number_of_clients, clients_start, clients_start)

    fuel_station = setOnePosition(
        walls, height, width, fuel_station, clients_start[0])[0]

    if (not simplified):
        airport = setOnePosition(walls, height, width,
                                 airport, fuel_station, clients_start[0])[0]
    taxi = setOnePosition(walls, height, width, taxi,
                          airport, fuel_station, clients_start[0])[1]
    clients_destination = setSeveralPositions(
        walls, height, width, number_of_clients, clients_destination, airport,fuel_station)

    return (clients_start,clients_destination) , fuel_station, airport, taxi


def setSeveralPositions(walls: Grid, height: int, width: int, n: int, position_to_change: Grid, *other_positions: Grid):

    is_available = False
    counter = 0
    client_positions = []
    # TODO Put positions only when there still are available places.
    while not is_available or counter < n:
        line = random.randint(0, height-1)
        column = random.randint(0, width-1)
        i = 0
        if len(other_positions) > 0:
            is_available = not walls[line][column] and not other_positions[i][line][column]
        else:
            is_available = not walls[line][column]
        while i < len(other_positions)-1 and is_available:
            is_available = not walls[line][column] and not other_positions[i+1][line][column]
            i += 1

        if is_available:
            position_to_change[line][column] = True
            client_positions.append((line, column))
            counter += 1
    

    return position_to_change, client_positions


def setOnePosition(walls: Grid, height: int, width: int, position_to_change: Grid, *other_positions: Grid):

    is_available = False
    while not is_available:
        line = random.randint(0, height-1)
        column = random.randint(0, width-1)
        i = 0
        if len(other_positions) > 0:

            is_available = not walls[line][column] and not other_positions[i][line][column]
        else:
            is_available = not walls[line][column]

        while i < len(other_positions)-1 and is_available:
            is_available = not walls[line][column] and not other_positions[i+1][line][column]
            i += 1

        if is_available:
            position_to_change[line][column] = True

    return position_to_change, (line, column)


def transformToStr(walls: Grid, clients: Grid, fuel_station: Grid, airport: Grid, taxi: Position) -> str:
    grid_str = "\n".join(["".join(["T" if (i == taxi[0] and j == taxi[1]) else ("%" if walls[i][j] else ("." if clients[0][0][i][j] else (
        "F" if fuel_station[i][j] else ("A" if airport[i][j] else " ")))) for j in range(len(walls[i]))]) for i in range(len(walls))])
    grid_str += f"\n {taxi[0]} {taxi[1]} 0"
    for i in range(len(clients[0][1])):
        grid_str += f"\n {clients[0][1][i][0]} {clients[0][1][i][1]}"
        grid_str += f" {clients[1][1][i][0]} {clients[1][1][i][1]}"
    return grid_str


if __name__ == '__main__':
    height, width = 10,10
    createLayout(3, height, width, 15, (height*width)*10, simplified=True,
                 directory_layout="simplified_layouts")
    createLayout(3, height, width, 15, (height*width)*10)
    pass
