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


def createLayout(number_of_layouts: int, height: int, width: int, number_of_stops: int, fuel_level: int, probability: float = 0.9, directory_layout: str ='files'+os.sep+ "layouts") -> None:
    try:
        os.mkdir(directory_layout)
    except OSError as error:
        print("{0} was not created as it already exists.".format(directory_layout))
    filename = directory_layout+os.sep+'_'+str(height)+'x'+str(width)+'_'
    for i in range(number_of_layouts):
        file = open(filename+str(i)+"_spawn.lay", "w+")
        walls = setWallsPositions(height, width, probability)
        stops, fuel_station, airport, taxi_position = setOtherPositions(
            walls, number_of_stops)

        grid_str = f"{height} {width} {number_of_stops} {fuel_level}\n"
        grid_str += transformToStr(walls, stops,
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


def setOtherPositions(walls: Grid, number_of_clients: int):
    height, width = len(walls), len(walls[0])
    fuel_station = [[False for j in range(width)] for i in range(height)]
    airport = [[False for j in range(width)] for i in range(height)]
    taxi = [[False for j in range(width)] for i in range(height)]
    stops = [[False for j in range(width)] for i in range(height)]
    
    stops = setSeveralPositions(
        walls, height, width, number_of_clients, stops, stops)

    fuel_station = setOnePosition(
        walls, height, width, fuel_station, stops[0])[0]
    airport = setOnePosition(walls, height, width,
                             airport, fuel_station, stops[0])
    taxi = setOnePosition(walls, height, width, taxi,
                          airport[0], fuel_station, stops[0])[1]

    return stops, fuel_station, airport, taxi


def setSeveralPositions(walls: Grid, height: int, width: int, number_of_elems: int, position_to_change: Grid, *other_positions: Grid):

    is_available = False
    counter = 0
    stops_positions = []
    # TODO Put positions only when there still are available places.
    while not is_available or counter < number_of_elems:
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
            spawn_probability = 1/number_of_elems   # TODO spawn probability to be a distribution over these 15 positions (the values sum up to 1).
            stops_positions.append((line, column, spawn_probability))
            counter += 1

    return position_to_change, stops_positions


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


def transformToStr(walls: Grid, stops: Grid, fuel_station: Grid, airport: Grid, taxi_position: Position, probability: int = 0.9) -> str:
   
    grid_str = "\n".join(["".join(["T" if (i == taxi_position[0] and j == taxi_position[1]) else ("%" if walls[i][j] else ("." if stops[0][i][j] else (
        "F" if fuel_station[i][j] else ("A" if airport[0][i][j] else " ")))) for j in range(len(walls[i]))]) for i in range(len(walls))])
    # grid_str += f"\n {taxi_position[0]} {taxi_position[1]} 1"
    grid_str += f"\n {airport[1][0]} {airport[1][1]} {probability}"

    for i in range(len(stops[1])):
        grid_str += f"\n {stops[1][i][0]} {stops[1][i][1]} {stops[1][i][2]}"
    return grid_str


if __name__ == '__main__':
    height, width = 5, 5
    
    createLayout(3, height, width, 3, (height*width)*10)
    pass
