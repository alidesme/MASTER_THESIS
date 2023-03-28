"""
Author      : DESMET Aline 
Matricule   : 000474868 (MA2-INFO)
Description : Generate prism file
"""

import stormpy
import os
import sys
import random
import copy


TEMP_DIR = 'files'+os.sep+'prism'
# os.mkdir(TEMP_DIR)
if not os.path.isdir(TEMP_DIR):
    # print('The directory',dirPath,'is not present. Creating a new one.')
    try:
        os.makedirs(TEMP_DIR)
    except:
        pass
else:
    pass
# try:
#     os.mkdir(TEMP_DIR)
# except OSError as error:
#     print("{0} was not created as it already exists.".format(TEMP_DIR))


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
        # print(layout_str)
    walls = [[layout_str[i][j] == "%" for j in range(
        len(layout_str[i]))] for i in range(len(layout_str))]
    stops = [[layout_str[i][j] == "." for j in range(
        len(layout_str[i]))] for i in range(len(layout_str))]
    fuel_station = [[layout_str[i][j] == "F" for j in range(
        len(layout_str[i]))] for i in range(len(layout_str))]
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
            # Taxi positions, Airport position & spawn prob, Stops positions &spawn prob
    f.close()
    return (walls, stops, fuel_station, airport, information, number_of_stops, fuel_level)


class taxiEngine:
    def __init__(self, walls, stops, fuel_station, airport, information, number_of_stops, fuel_level, prism_filename=None):
        self.height = len(walls)
        self.width = len(walls[0])
        self.walls = walls
        self.stops = stops
        self.fuel_station = fuel_station
        self.fuel_level = fuel_level
        self.airport = airport
        self.information = information
        self.number_of_stops = number_of_stops
        self.prism_filename = prism_filename

    def _openOutput(self):
        if self.prism_filename == None:
            self.prism_out = sys.stdout
        else:
            file = open(self.prism_filename, 'w+')
            self.prism_out = file

    def _initialize(self):
        print('mdp\n', file=self.prism_out)

        print(f'int totalFuel = {self.fuel_level};', file=self.prism_out)
        # Day = 0-8 ]10-16,18-20] Pick = 9-14 ]6-10 & 16-18] Night = 15-24 ]20-6]
        print(f'int timeOfTheDay = 0;', file=self.prism_out)
        print(f'const int jamDay = 2;', file=self.prism_out)  # 2
        print(f'const int jamPick = 4;', file=self.prism_out)  # 4
        print(f'const int jamNight = 1;', file=self.prism_out)  # 1
        print(f'int jamCounter = 0;', file=self.prism_out)  #

        for i in range(self.height):
            for j in range(self.width):
                """
                constant wi_j is 1 if there is a wall in (i,j)th coordinate
                constant hi_j is 1 if there is a hole in (i,j)th coordinate
                constant ti_j is 1 if there is a target in (i,j)th coordinate
                constant xi_j = i and yi_j = j 
                """
                print(f'const int x{i}_{j} = {i};', file=self.prism_out)
                print(f'const int y{i}_{j} = {j};', file=self.prism_out)
                print(
                    f'const int w{i}_{j} = {int(self.walls[i][j])};', file=self.prism_out)
                print(
                    f'const int s{i}_{j} = {int(self.stops[i][j])};', file=self.prism_out)
                print(
                    f'const int f{i}_{j} = {int(self.fuel_station[i][j])};', file=self.prism_out)
                print(
                    f'const int a{i}_{j} = {int(self.airport[i][j])};', file=self.prism_out)

    def _moduleArbiter(self):
        print('\nmodule arbiter\n', file=self.prism_out)
        print(f'token : [0 .. 6] init 0;', file=self.prism_out)
        '''
            1 token for jam
            1 token for taxi position
            1 token for client1
            1 token for client2
            1 token for fuel
            1 token for day
        
            '''

        print('[updateJam] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[East] (token = 2) -> 1: (token\' = 3);', file=self.prism_out)
        print('[West] (token = 2) -> 1: (token\' = 3);', file=self.prism_out)
        print('[North] (token = 2) -> 1: (token\' = 3);', file=self.prism_out)
        print('[South] (token = 2) -> 1: (token\' = 3);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[client0] (token = 3) -> 1: (token\' = 4);', file=self.prism_out)
        print('[client1] (token = 4) -> 1: (token\' = 5);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[updateFuel] (token = 5) -> 1: (token\' = 6);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[updateDay] (token = 6) -> 1: (token\' = 0);', file=self.prism_out)

        print('\nendmodule\n', file=self.prism_out)

    def _taxiMove(self):

        formulaLoss = 'formula loss = '  # If no more fuel
        formulaNorth = 'formula north = '
        formulaSouth = 'formula south = '
        formulaEast = 'formula east = '
        formulaWest = 'formula west = '
        formulaReward = 'formula reward = '

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

        # if the taxi arrived to the client1's destination or client2's destination
        formulaReward += f'(xt = xd1 & yt = yd1) | (xt = xd2 & yt = yd2)'+';\n'

        # if the taxi is out of fuel
        formulaLoss += f'!(xt = xf & yt = yf) & (totalFuel = 0)'+';\n'

        formulaNorth = formulaNorth[:-3]+';\n'
        formulaSouth = formulaSouth[:-3]+';\n'
        formulaEast = formulaEast[:-3]+';\n'
        formulaWest = formulaWest[:-3]+';\n'
        # formulaReward = formulaReward[:-3]+';\n'
        # formulaLoss = formulaLoss[:-3]+';\n'
        print(formulaNorth, file=self.prism_out)
        print(formulaSouth, file=self.prism_out)
        print(formulaEast, file=self.prism_out)
        print(formulaWest, file=self.prism_out)
        print(formulaReward, file=self.prism_out)
        print(formulaLoss, file=self.prism_out)

    def _jamUpdate(self):
        print(f'\nmodule jam\n', file=self.prism_out)
        print(f'formula day = (timeOfTheDay <= 8);\n', file=self.prism_out)
        print(f'formula pick = ((timeOfTheDay > 8) & (timeOfTheDay <= 14));\n',
              file=self.prism_out)
        print(f'formula night = ((timeOfTheDay > 14) & (timeOfTheDay <= 24));\n',
              file=self.prism_out)
        print(f'[updateJam] (day) -> 1: jamCounter\' = jamDay;',
              file=self.prism_out)
        print(f'[updateJam] (pick) -> 1: jamCounter\' = jamPick;',
              file=self.prism_out)
        print(f'[updateJam] (night) -> 1: jamCounter\' = jamNight;',
              file=self.prism_out)
        print(f'[updateDay] true -> 1: timeOfTheDay\' = timeOfTheDay + 1;',
              file=self.prism_out)
        print(f'formula jam = ((day | pick | night) & jamCounter > 0);\n',
              file=self.prism_out)
        print('\nendmodule\n', file=self.prism_out)

    def _moduleTaxi(self):
        print('\nmodule taxi\n', file=self.prism_out)
        position_taxi = (self.information[0][0][0], self.information[0][0][1])

        print(
            f'xt : [1..{self.height-1}] init {position_taxi[0]};', file=self.prism_out)
        print(
            f'yt : [1..{self.width-1}] init {position_taxi[1]};\n', file=self.prism_out)
        self._taxiMove()
        print("[East] (east) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (yt'=yt+1) & (jamCounter' = 0) & (totalFuel' = totalFuel-1);", file=self.prism_out)
        print("[West] (west) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (yt'=yt-1) & (jamCounter' = 0)  & (totalFuel' = totalFuel-1);", file=self.prism_out)
        print("[North] (north) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (xt' = xt -1) & (jamCounter'= 0) & (totalFuel' = totalFuel-1);", file=self.prism_out)
        print("[South] (south) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (xt'= xt+1) & (jamCounter' = 0)  & (totalFuel' = totalFuel-1);", file=self.prism_out)
        print(
            f'[updateFuel] (xf = xt & yf = yt) -> 1: totalFuel = {self.fuel_level};', file=self.prism_out)
        # print("[] (win | loss) -> 1 : (end' = true);", file=self.prism_out)
        print('\nendmodule\n', file=self.prism_out)

    def _moduleClient(self, k):
        print(f'\nmodule client_{k}\n', file=self.prism_out)
        # temp = copy.deepcopy(self.information[2:])
        # print(temp)
        # temp_probability = random.choices(
        #     temp, weights=[temp[i][1] for i in range(len(temp))], k=len(temp))
        # random_start_position = random.choice(temp_probability)
        # # random_start_position = random.choice(temp)

        # print("?????", random_start_position)
        # temp.pop(temp.index(random_start_position))
        random_start_position,random_destination_position = self.setRandomPositions()

        print(
            f'xc_{k} : [1..{self.height-1}] init {random_start_position[0]};', file=self.prism_out)
        print(
            f'yc_{k} : [1..{self.width-1}] init {random_start_position[1]};\n', file=self.prism_out)

        # print(f'xd1 : [1..{height-1}] init {random_destination_position[0]};', file=self.prism_out)
        # print(f'yd1 : [1..{width-1}] init {random_destination_position[1]};\n', file=self.prism_out)

        # TODO Random waiting time ???
        print(f'int totalWaiting_{k} = 5;', file=self.prism_out)

        print(
            f'formula waiting_{k} = totalWaiting_{k} > 0;\n', file=self.prism_out)
        print(
            f'formula riding_{k} = (xc_{k} = xt) & (yc_{k} = yt);\n', file=self.prism_out)
        print(
            f'formula reaching_{k} = (xt = {random_destination_position[0]}) &(yt = {random_destination_position[1]});\n', file=self.prism_out)

        print(f'[client_{k}] (waiting_{k}) -> 1: xc_{k}\' = xc_{k} & yc_{k}\' = yc_{k} & totalWaiting_{k}\' = totalWaiting_{k} - 1 ;', file=self.prism_out)
        print(
            f'[client_{k}] (riding_{k}) -> 1: xc_{k}\' = xt & yc_{k}\' = yt;', file=self.prism_out)

        random_start_position = self.setRandomPositions()[0]

        print(f'[client_{k}] (!(waiting_{k}) & !(riding_{k}) & !(reaching_{k})) | (reaching_{k}) -> 1:xc_{k}={random_start_position[0]} & yc_{k}={random_start_position[1]}& totalWaiting_{k} = 5 ;', file=self.prism_out)

        print('\nendmodule\n', file=self.prism_out)

    def setRandomPositions(self):
        temp = copy.deepcopy(self.information[2:])
        temp_probability = random.choices(
            temp, weights=[temp[i][1] for i in range(len(temp))], k=len(temp))
        random_start_position = random.choice(temp_probability)

        temp.pop(temp.index(random_start_position))
        random_start_position = random_start_position[0]
        random_destination_position = random.choice(temp)[0]
        return random_start_position, random_destination_position

    def createPrismFilefFromGrids(self):
        self._openOutput()
        self._initialize()
        self._jamUpdate()
        self._moduleArbiter()

        self._moduleTaxi()
        for k in range(2):
            self._moduleClient(k)
        return (self.prism_filename)


def createEngine(layout_filename):
    walls, stops, fuel_station, airport, information, number_of_stops, fuel_level = readFromFile(
        layout_filename)
    prism_filename = TEMP_DIR+os.sep+str(os.getpid())+f'_{number_of_stops}.nm'
    t = taxiEngine(walls, stops, fuel_station, airport,
                   information, number_of_stops, fuel_level, prism_filename)
    t.createPrismFilefFromGrids()


    # print(t)
if __name__ == '__main__':
    createEngine("layouts/_10x10_0_spawn.lay")
    pass

    # print('\nmodule client2\n', file=self.prism_out)
    # temp = copy.deepcopy(information[2:])
    # random_start_position = random.choice(temp)[0]
    # temp.pop(random_start_position)
    # random_destination_position = random.choice(temp)[0]

    # print(f'xc2 : [1..{height-1}] init {random_start_position[0]};', file=self.prism_out)
    # print(f'yc2 : [1..{width-1}] init {random_start_position[1]};\n', file=self.prism_out)

    # # print(f'xd1 : [1..{height-1}] init {random_destination_position[0]};', file=self.prism_out)
    # # print(f'yd1 : [1..{width-1}] init {random_destination_position[1]};\n', file=self.prism_out)

    # print(f'int totalWaiting2 = 5;', file=self.prism_out)  #TODO Random waiting time ???

    # print(f'formula waiting = totalWaiting2 > 0;\n', file=self.prism_out)
    # print(f'formula riding = (xc2 = xt) & (yc2 = yt);\n', file=self.prism_out)
    # print(f'formula reaching = ({random_destination_position[0]} = xt) &({random_destination_position[1]} = yt);\n', file=self.prism_out)

    # print(f'[client2] (waiting) -> 1: xc2\' = xc2 & yc2\' = yc2 & totalWaiting1\' = totalWaiting1-1 ;',file=self.prism_out)
    # print(f'[client2] (riding) -> 1: xc2\' = xt & yc2\' = yt;',file=self.prism_out)

    # temp = copy.deepcopy(information[2:])
    # random_start_position = random.choice(temp)[0]
    # temp.pop(random_start_position)
    # random_destination_position = random.choice(temp)[0]
    # print(f'[client2] (!(waiting) & !(riding) & !(reaching)) | (reaching) -> 1:xc2={random_start_position} & yc2={random_destination_position}& totalWaiting1 = 5 ;',file=self.prism_out)

    # print('\nendmodule\n', file=self.prism_out)

    # print('rewards', file=self.prism_out)
    # print('[East] true : -1;', file=self.prism_out)
    # print('[West] true: -1;', file=self.prism_out)
    # print('[North] true: -1;', file=self.prism_out)
    # print('[South] true: -1;', file=self.prism_out)
    # print('(win & !end) : 100;', file=self.prism_out)
    # print('(loss & !end) : -100;', file=self.prism_out)
    # print('endrewards\n', file=self.prism_out)

    # print('label "win" = win;', file=self.prism_out)
    # print('label "loss" = loss;', file=self.prism_out)
