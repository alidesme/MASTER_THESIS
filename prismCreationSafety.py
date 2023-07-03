"""
Author      : DESMET Aline 
Matricule   : 000474868 (MA2-INFO)
Description : Generate Safety prism file
"""

import stormpy
import gc
import os
import sys
import random
import copy


TEMP_DIR = 'files'+os.sep+'prismSafety'
# os.mkdir(TEMP_DIR)
if not os.path.isdir(TEMP_DIR):
    try:
        os.makedirs(TEMP_DIR)
    except:
        pass
else:
    pass


def readFromFile(layout_filename):

    f = open(layout_filename)
    line = f.readline().split()
    if len(line) > 4:
        raise Exception("Size mismatch : "+str(line))
    else:
        X = int(line[0])
        Y = int(line[1])
        number_of_stops = int(line[2])
        fuel_level = int(line[3])
    layout_str = []
    for i in range(X):
        layout_str.append(f.readline().strip('\n'))

    taxi = findPosition(layout_str, "T")

    walls = [[layout_str[i][j] == "%" for j in range(
        len(layout_str[i]))] for i in range(len(layout_str))]

    stops = [[layout_str[i][j] == "." for j in range(
        len(layout_str[i]))] for i in range(len(layout_str))]

    fuel_station = [[layout_str[i][j] == "F" for j in range(
        len(layout_str[i]))] for i in range(len(layout_str))]
    fuel_position = findPosition(layout_str, "F")

    airport = [[layout_str[i][j] == "A" for j in range(
        len(layout_str[i]))] for i in range(len(layout_str))]

    information = []
    for i in range(number_of_stops+1):
        str_information = f.readline().split()
        if len(str_information) > 3:
            raise Exception("Size mismatch : "+str(str_information))
        else:
            information.append([(int(str_information[0]), int(
                str_information[1])), float(str_information[2])])
            # Airport position & spawn prob, Stops positions &spawn prob
    f.close()
    return (taxi, walls, airport, stops, number_of_stops, fuel_station, fuel_position, fuel_level, information)


def findPosition(grid, letter):
    i = 0
    j = 0
    position_found = False
    while i < len(grid) and not position_found:
        j = 0
        while j < len(grid[0]) and not position_found:
            if grid[i][j] == letter:
                position_found = True
                position = (i, j)
            j += 1
        i += 1
    return position


class taxiEngine:
    def __init__(self, taxi, walls, fuel_station, fuel_position, fuel_level, information, prism_filename=None):
        self.height = len(walls)
        self.width = len(walls[0])
        self.taxi = taxi
        self.walls = walls
        self.fuel_station = fuel_station
        self.fuel_position = fuel_position
        self.fuel_level = fuel_level
        self.information = information
        self.prism_filename = prism_filename

    def _openOutput(self):
        if self.prism_filename == None:
            self.prism_out = sys.stdout
        else:
            file = open(self.prism_filename, 'w+')
            self.prism_out = file

    def _initialize(self):
        print('mdp\n', file=self.prism_out)
        print(f'global totalFuel : int init {self.fuel_level};', file=self.prism_out)
        print(f'global timeOfTheDay : int init 0;', file=self.prism_out)

        for i in range(self.height):
            for j in range(self.width):
                """
                constant wi_j is 1 if there is a wall in (i,j)th coordinate
                constant xi_j = i and yi_j = j 
                """
                print(f'const int x{i}_{j} = {i};', file=self.prism_out)
                print(f'const int y{i}_{j} = {j};', file=self.prism_out)
                print(
                    f'const int w{i}_{j} = {int(self.walls[i][j])};', file=self.prism_out)
        print(f'const int xf = {self.fuel_position[0]};', file=self.prism_out)
        print(f'const int yf = {self.fuel_position[1]};\n', file=self.prism_out)
        
        print("formula fuelOK = (totalFuel >= 1)?1:0;", file=self.prism_out)
        print("formula unsafe = (fuelOK = 0);\n", file=self.prism_out)

        
        self._taxiMove()

        self._dayHours()

    def _dayHours(self):
        print(f'formula day_hours = (timeOfTheDay <= 8);', file=self.prism_out)
        print(f'formula pick_hours = (timeOfTheDay > 8) & (timeOfTheDay <= 14);',
              file=self.prism_out)
        print(f'formula night_hours = (timeOfTheDay > 14) & (timeOfTheDay <= 24);',
              file=self.prism_out)

  
   
    def _moduleArbiter(self):
        print('\nmodule arbiter\n', file=self.prism_out)
        print(f'token : [0 .. 2] init 0;', file=self.prism_out)
        '''
            1 token for taxi position
            1 token for fuel
            1 token for day
        
            '''

        print('', file=self.prism_out)
        print('[North] (token = 0) -> 1: (token\' = 1);', file=self.prism_out)
        print('[South] (token = 0) -> 1: (token\' = 1);', file=self.prism_out)
        print('[East] (token = 0) -> 1: (token\' = 1);', file=self.prism_out)
        print('[West] (token = 0) -> 1: (token\' = 1);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[updateFuel] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[updateDay] (token = 2) -> 1: (token\' = 0);', file=self.prism_out)

        print('\nendmodule\n', file=self.prism_out)

    def _taxiMove(self):

        formulaNorth = 'formula north = '
        formulaSouth = 'formula south = '
        formulaEast = 'formula east = '
        formulaWest = 'formula west = '

        for i in range(self.height):
            for j in range(self.width):

                if i > 0:
                    # if there is no wall in the north
                    formulaNorth += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i-1}_{j} = 0) | '
                if i < self.height-1:
                    # if there is no wall in the south
                    formulaSouth += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i+1}_{j} = 0) | '
                if j < self.width-1:
                    # if there is no wall in the east
                    formulaEast += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i}_{j+1} = 0) | '
                if j > 0:
                    # if there is no wall in the west
                    formulaWest += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i}_{j-1} = 0) | '

        formulaNorth = formulaNorth[:-3]+';'
        formulaSouth = formulaSouth[:-3]+';'
        formulaEast = formulaEast[:-3]+';'
        formulaWest = formulaWest[:-3]+';'

        print(formulaNorth, file=self.prism_out)
        print(formulaSouth, file=self.prism_out)
        print(formulaEast, file=self.prism_out)
        print(formulaWest, file=self.prism_out)
        print()

    def _moduleFuel(self):
        print('\nmodule fuel\n', file=self.prism_out)
        # position_taxi = (self.information[0][0][0], self.information[0][0][1])

        print(
            f'[updateFuel] (xt = xf & yt = yf) -> 1: (totalFuel\' = {self.fuel_level});', file=self.prism_out)
        print(
            f'[updateFuel] !(xt = xf & yt = yf) -> 1: (totalFuel\' = totalFuel);', file=self.prism_out)
        print('\nendmodule\n', file=self.prism_out)

    def _moduleTaxi(self):
        print('\nmodule taxi\n', file=self.prism_out)
        print(
            f'xt : [1..{self.height-1}] init {self.taxi[0]};', file=self.prism_out)
        print(
            f'yt : [1..{self.width-1}] init {self.taxi[1]};\n', file=self.prism_out)

        print("[North] (north) -> (fuelOK): (xt' = xt - 1) & (totalFuel' = totalFuel-1) + (1 - fuelOK) : (xt' = xt);", file=self.prism_out) # TODO Keep 1-fuelOK or not ??
        print("[South] (south) -> (fuelOK): (xt'= xt + 1) & (totalFuel' = totalFuel-1) + (1 - fuelOK) : (xt' = xt);", file=self.prism_out)
        print("[East] (east) -> (fuelOK): (yt' = yt + 1) & (totalFuel' = totalFuel-1) + (1 - fuelOK) : (yt' = yt);", file=self.prism_out)
        print("[West] (west) -> (fuelOK): (yt' = yt - 1) & (totalFuel' = totalFuel-1) + (1 - fuelOK) : (yt' = yt);", file=self.prism_out)

        print('\nendmodule\n', file=self.prism_out)

    def _moduleTime(self):
        print('\nmodule time\n', file=self.prism_out)
        print("[updateDay] true -> (timeOfTheDay' = (timeOfTheDay + 1) % 24);",
              file=self.prism_out)
        print('\nendmodule\n', file=self.prism_out)

 
    def _rewards(self):
        print('rewards "r"', file=self.prism_out)
        print(
                f'((xt = xf & yt = yf) & token = 1): 50;', file=self.prism_out)
        print('endrewards\n', file=self.prism_out)

    def createPrismFilefFromGrids(self):
        self._openOutput()
        self._initialize()
        self._moduleTime()
        self._moduleFuel()
        self._moduleArbiter()
        self._moduleTaxi()

        return (self.prism_filename)


def createEngine(layout_filename):
    taxi, walls, airport, stops, number_of_stops, fuel_station, fuel_position, fuel_level, information = readFromFile(
        layout_filename)
    prism_filename = TEMP_DIR+os.sep+str(os.getpid())+f'_{number_of_stops}.nm'
    t = taxiEngine(taxi, walls, fuel_station, fuel_position, fuel_level, information, prism_filename)
    return t.createPrismFilefFromGrids()


def getValue(prismFile, formula_str='Pmax=? [G !(unsafe)] '):
    prism_program = stormpy.parse_prism_program(prismFile)
    properties = stormpy.parse_properties(formula_str, prism_program)

    model = stormpy.build_model(prism_program, properties)
    print(f"With '{formula_str}', here is the model:\n")
    print(model)
    result = stormpy.model_checking(
        model, properties[0], only_initial_states=True)
    # assert result.result_for_all_states
    initial_state = model.initial_states[0]
    value = result.at(initial_state)
    del model

    gc.collect()
    return (value)


if __name__ == '__main__':
    p = createEngine("files/layouts/_10x10_0_spawn.lay")
    print(getValue(p))
    # print(getValue("files/prismSafety/363908_15.nm"))  # With Safety

    pass
