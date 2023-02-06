"""
Author      : DESMET Aline 
Matricule   : 000474868 (MA2-INFO)
Description : Generate random layouts
"""

import random
import os
from typing import List, Tuple

Grid = List[List[bool]]
Position = Tuple[int, int]
def createLayout(number_of_layouts:int, height:int, width:int, directory_layout:str, probability:float=0.9) -> None:
    try:
        os.mkdir(directory_layout)
    except OSError as error:
        print("{0} was not created as it already exists.".format(directory_layout))
    filename = directory_layout+os.sep+'_'+str(height)+'x'+str(width)+'_'
    for i in range(number_of_layouts):
        file = open(filename+str(i)+".lay", "w+")
        walls = setWallsPositions(height, width, probability)
        clients, gaz_station, airport, taxi_position = setPositions(
            walls, probability)
        draw_horizon= 2*(height+width)
        grid_str= transformToStr(walls, clients, gaz_station, airport, taxi_position, draw_horizon)
        print(grid_str, file=file)
        file.close()


def setWallsPositions(height:int, width:int, probability:float=0.9) -> Grid:

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


def setPositions(walls:Grid, probability:float=0.9):
    height, width = len(walls), len(walls[0])
    gaz_station = [[False for j in range(width)] for i in range(height)]
    airport = [[False for j in range(width)] for i in range(height)]
    taxi = [[False for j in range(width)] for i in range(height)]
    clients = []
    for i in range(height):
        row = []
        for j in range(width):
            random_probability = random.random()
            if walls[i][j]:
                row.append(False)
            elif random_probability > probability:
                row.append(True)
            else:
                row.append(False)
        clients.append(row)

    gaz_station = setOnePosition(walls, height, width, gaz_station, clients)[0]
    airport = setOnePosition(walls, height, width, airport, gaz_station, clients)[0]
    taxi = setOnePosition(walls, height, width, taxi,
                    airport, gaz_station, clients)[1]

    return clients, gaz_station, airport, taxi


def setOnePosition(walls:Grid, height:int, width:int, position_to_change:Grid, *other_positions:Grid):

    is_available = False
    while not is_available:
        line = random.randint(0, height-1)
        column = random.randint(0, width-1)
        i = 0
        is_available = not walls[line][column] and not other_positions[i][line][column]

        while i < len(other_positions)-1 and is_available:
            is_available = not walls[line][column] and not other_positions[i+1][line][column]
            i += 1

        if is_available:
            position_to_change[line][column] = True

    return position_to_change, (line, column)

def transformToStr(walls: Grid, clients: Grid, gaz_station: Grid, airport:Grid, taxi:Position, draw_horizon:int, discount:int=1) -> str:
    grid_str = "\n".join(["".join(["P" if (i == taxi[0] and j == taxi[1]) else ("%" if walls[i][j] else ("." if clients[i][j] else ("G" if gaz_station[i][j] else ("A" if airport[i][j] else " ")))) for j in range(len(walls[i]))]) for i in range(len(walls))])
    grid_str+= '\nParameters\ndraw '+str(draw_horizon)+'\ndiscount '+str(discount)+'\nInitPosition\n'+str(taxi)
    return grid_str

if __name__ == '__main__':
    createLayout(3, 50, 70, "layouts", probability=0.9)
    pass
