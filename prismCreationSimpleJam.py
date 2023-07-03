"""
Author      : DESMET Aline 
Matricule   : 000474868 (MA2-INFO)
Description : Generate prism file
"""

import stormpy
import gc
import os
import sys
import random
import copy


TEMP_DIR = 'files'+os.sep+'prismSJam'
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
    def __init__(self, taxi, walls, number_of_clients, airport, stops, number_of_stops, fuel_station, fuel_position, fuel_level, information, prism_filename=None):
        self.height = len(walls)
        self.width = len(walls[0])
        self.taxi = taxi
        self.walls = walls
        self.number_of_clients = number_of_clients
        self.airport = airport
        self.stops = stops
        self.number_of_stops = number_of_stops
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

        print(f'global timeOfTheDay : int init 0;', file=self.prism_out)
        print(f'global jamCounter : int init -1;\n', file=self.prism_out)  #

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

        formulaBusy = "formula busy = "
        for k in range(self.number_of_clients):
            self._client(k)
            formulaBusy += f'c{k}_in + '
        formulaBusy = formulaBusy[:-3] + ';\n'
        print(formulaBusy, file=self.prism_out)

        self._taxiMove()

        self._jam()
        self._dayHours()

    def _dayHours(self):
        print(f'formula day_hours = (timeOfTheDay <= 8);', file=self.prism_out)
        print(f'formula pick_hours = (timeOfTheDay > 8) & (timeOfTheDay <= 14);',
              file=self.prism_out)
        print(f'formula night_hours = (timeOfTheDay > 14) & (timeOfTheDay <= 24);',
              file=self.prism_out)

    def _jam(self):
        print(f'const int jamDay = 2;', file=self.prism_out)  # 2
        print(f'const int jamPick = 3;', file=self.prism_out)  # 4
        print(f'const int jamNight = 1;\n', file=self.prism_out)  # 1
        print(f'formula jam = (jamCounter >= 0);',
              file=self.prism_out)  # OK TODO Is "jam" accessible in other module ? ANSWER : YES f it is defined outside a module
        print(f'formula jam_int = (jamCounter != 0)?1:0;\n',
              file=self.prism_out)

    def _client(self, k):
        formulaPicking = f"formula picking_c{k} = (xt = xs_c{k}) & (yt = ys_c{k}) & (busy = 0);"
        print(formulaPicking, file=self.prism_out)

        # if the taxi arrived to the client0's destination or client1's destination
        print(
            f'formula reaching_c{k} = (xt = xd_c{k}) & (yt = yd_c{k}) & (c{k}_in = 1);', file=self.prism_out)
        print(
            f"formula riding_c{k} =  !(picking_c{k}) & !(reaching_c{k});\n", file=self.prism_out)

        print(
            f"formula distanceX_c{k} = max(xs_c{k}-xd_c{k},xd_c{k}-xs_c{k});", file=self.prism_out)
        print(
            f"formula distanceY_c{k} = max(ys_c{k}-yd_c{k},yd_c{k}-ys_c{k});\n", file=self.prism_out)

    def _moduleArbiter(self):
        print('\nmodule arbiter\n', file=self.prism_out)
        print(f'token : [0 .. 6] init 0;', file=self.prism_out)
        '''
            1 token for jam
            1 token for taxi position
            1 token for pick0
            1 token for pick1
            1 token for client0
            1 token for client1
            1 token for day
        
            '''
        print('', file=self.prism_out)
        print('[updateJam] (token = 0) -> 1: (token\' = 1);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[North] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)
        print('[South] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)
        print('[East] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)
        print('[West] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[pick_0] (token = 2) -> 1: (token\' = 3);', file=self.prism_out)
        print('[pick_1] (token = 3) -> 1: (token\' = 4);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[client_0] (token = 4) -> 1: (token\' = 5);', file=self.prism_out)
        print('[client_1] (token = 5) -> 1: (token\' = 6);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[updateDay] (token = 6) -> 1: (token\' = 0);', file=self.prism_out)

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

    def _moduleJam(self):
        print('\nmodule jam\n', file=self.prism_out)
        # position_taxi = (self.information[0][0][0], self.information[0][0][1])

        print(f'[updateJam] (day_hours & jamCounter = -1) -> 1: (jamCounter\' = jamDay);',
              file=self.prism_out)
        print(f'[updateJam] (pick_hours & jamCounter = -1) -> 1: (jamCounter\' = jamPick);',
              file=self.prism_out)
        print(f'[updateJam] (night_hours & jamCounter = -1) -> 1: (jamCounter\' = jamNight);',
              file=self.prism_out)
        print(f'[updateJam] (jam) -> 1: (jamCounter\' = jamCounter);',
              file=self.prism_out)

        print('\nendmodule\n', file=self.prism_out)

    def _moduleTaxi(self):
        print('\nmodule taxi\n', file=self.prism_out)

        print(
            f'xt : [1..{self.height-1}] init {self.taxi[0]};', file=self.prism_out)
        print(
            f'yt : [1..{self.width-1}] init {self.taxi[1]};\n', file=self.prism_out)

        print("[North] (north) -> (jam_int): (jamCounter' = jamCounter - 1) +  (1 - jam_int) : (xt' = xt - 1) & (jamCounter\' = - 1);", file=self.prism_out)
        print("[South] (south) -> (jam_int): (jamCounter' = jamCounter - 1) +  (1 - jam_int) : (xt'= xt + 1) & (jamCounter\' = - 1);", file=self.prism_out)
        print("[East] (east) -> (jam_int): (jamCounter' = jamCounter - 1) +  (1 - jam_int) : (yt' = yt + 1) & (jamCounter\' = - 1);", file=self.prism_out)
        print("[West] (west) -> (jam_int): (jamCounter' = jamCounter - 1) +  (1 - jam_int) : (yt' = yt - 1) & (jamCounter\' = - 1);", file=self.prism_out)

        print('\nendmodule\n', file=self.prism_out)

    def _moduleTime(self):
        print('\nmodule time\n', file=self.prism_out)
        print("[updateDay] true -> (timeOfTheDay' = (timeOfTheDay + 1) % 24);",
              file=self.prism_out)
        print('\nendmodule\n', file=self.prism_out)

    def _moduleClient(self):
        for k in range(self.number_of_clients):
            print(f'\nmodule client{k}\n', file=self.prism_out)

            random_start_position, random_destination_position = self.setRandomClientAttributes()

            print(
                f'xs_c{k} : [1..{self.height-1}] init {random_start_position[0]};', file=self.prism_out)
            print(
                f'ys_c{k} : [1..{self.width-1}] init {random_start_position[1]};\n', file=self.prism_out)
            print(
                f'xc_c{k} : [1..{self.height-1}] init {random_start_position[0]};', file=self.prism_out)
            print(
                f'yc_c{k} : [1..{self.width-1}] init {random_start_position[1]};\n', file=self.prism_out)
            print(
                f'xd_c{k} : [1..{self.height-1}] init {random_destination_position[0]};', file=self.prism_out)
            print(
                f'yd_c{k} : [1..{self.width-1}] init {random_destination_position[1]};\n', file=self.prism_out)
            print(
                f'c{k}_in : [0..1] init 0;\n', file=self.prism_out)

            print(
                f'[pick_{k}] (c{k}_in = 1) -> (xc_c{k}\' = xt) & (yc_c{k}\' = yt);', file=self.prism_out)  # TODO allows to update current position of the client
            print(
                f'[pick_{k}] (c{k}_in = 0) -> (xc_c{k}\' = xs_c{k}) & (yc_c{k}\' = ys_c{k});\n', file=self.prism_out)

            print(
                f'[client_{k}] (picking_c{k}) -> 1: (c{k}_in\' = 1);', file=self.prism_out)

            print(f'[client_{k}] (reaching_c{k}) -> ' +
                  self.setClientNewPositions(k), file=self.prism_out)

            print(f'[client_{k}] (riding_c{k}) -> 1: (xs_c{k}\' = xs_c{k}) & (ys_c{k}\' = ys_c{k}) & (xd_c{k}\' = xd_c{k}) & (yd_c{k}\' = yd_c{k}) & (xc_c{k}\' = xc_c{k}) & (yc_c{k}\' = yc_c{k});', file=self.prism_out)
            # TODO redundacy ... must simplify bc same as ck in??
            print('\nendmodule\n', file=self.prism_out)

    def setClientNewPositions(self, k):
        client_position = f''
        # print(temp)
        for i in range(len(self.information)):
            client_position += f'{self.information[i][1]} : (xs_c{k}\' = {self.information[i][0][0]}) & (ys_c{k}\' = {self.information[i][0][1]}) & '
            temp = copy.deepcopy(self.information)
            # print(i)
            temp.pop(temp.index(self.information[i]))
            if len(temp) > 0:
                random_destination_position = random.choice(temp)[0]
                client_position += f'(xd_c{k}\' = {random_destination_position[0]}) & (yd_c{k}\' = {random_destination_position[1]}) & (c{k}_in\' = 0) + '

        return client_position[:-3]+';'

    def setRandomClientAttributes(self):
        temp = copy.deepcopy(self.information)
        temp_probability = random.choices(
            temp, weights=[temp[i][1] for i in range(len(temp))], k=len(temp))
        random_start_position = random.choice(temp_probability)
        position_to_pop = temp.index(random_start_position)
        temp.pop(position_to_pop)
        random_start_position = random_start_position[0]
        random_destination_position = random.choice(
            temp)[0]  # OK TODO airport IS in destination too

        return random_start_position, random_destination_position

    def _rewards(self):
        print('rewards "r"', file=self.prism_out)
        for k in range(self.number_of_clients):
            print(
                f'(reaching_c{k} & token = {k+4}): distanceX_c{k} + distanceY_c{k};', file=self.prism_out)
        print('endrewards\n', file=self.prism_out)

    def createPrismFilefFromGrids(self):
        # number_of_clients = 2
        self._openOutput()
        self._initialize()
        self._moduleTime()
        self._moduleJam()
        self._moduleArbiter()
        self._moduleTaxi()
        self._moduleClient()

        self._rewards()
        return (self.prism_filename)


def createEngine(layout_filename):
    taxi, walls, airport, stops, number_of_stops, fuel_station, fuel_position, fuel_level, information = readFromFile(
        layout_filename)
    prism_filename = TEMP_DIR+os.sep+str(os.getpid())+f'_{number_of_stops}.nm'
    number_of_clients = 2
    t = taxiEngine(taxi, walls, number_of_clients, airport, stops, number_of_stops,
                   fuel_station, fuel_position, fuel_level, information, prism_filename)
    return t.createPrismFilefFromGrids()


# TODO What to satisfy ? #  R{"r"}max=? [F ((busy=1) )]"Rmax=? [LRA]"& (((1-jam_int) * fuelOK)= 1) & jamCounter = 0 &
def getValue(prismFile, formula_str='R{"r"}max=? [F (reaching_c0 & token = 4)] '):
    prism_program = stormpy.parse_prism_program(prismFile)
    properties = stormpy.parse_properties(formula_str, prism_program)

    model = stormpy.build_model(prism_program, properties)
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
    # print(getValue(p))

    # print(getValue("files/prismSJam/179855_3.nm"))  # With jam

    pass
