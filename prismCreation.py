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


TEMP_DIR = 'files'+os.sep+'prism'
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
        self.fuel_position =fuel_position
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
        # Day = 0-8 ]10-16,18-20] Pick = 9-14 ]6-10 & 16-18] Night = 15-24 ]20-6]
        print(f'global timeOfTheDay : int init 0;', file=self.prism_out)
        print(f'global jamCounter : int init 0;\n', file=self.prism_out)  #

        print(f'const int jamDay = 2;', file=self.prism_out)  # 2
        print(f'const int jamPick = 4;', file=self.prism_out)  # 4
        print(f'const int jamNight = 1;\n', file=self.prism_out)  # 1

        print(f'const int xf = {self.fuel_position[0]};', file=self.prism_out)
        print(f'const int yf = {self.fuel_position[1]};\n', file=self.prism_out)

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
                    f'const int s{i}_{j} = {int(self.stops[i][j])};', file=self.prism_out)  # TODO Not necessary ?
                print(
                    f'const int f{i}_{j} = {int(self.fuel_station[i][j])};', file=self.prism_out)
                print(
                    f'const int a{i}_{j} = {int(self.airport[i][j])};', file=self.prism_out)
                
        formulaBusy = 'formula busy = '
            
        for k in range(self.number_of_clients):

            print('\n'+f"formula distanceX_c{k} = max(xs_c{k}-xd_c{k},xd_c{k}-xs_c{k});", file= self.prism_out)
            print(f"formula distanceY_c{k} = max(ys_c{k}-yd_c{k},yd_c{k}-ys_c{k});", file=self.prism_out)
            formulaBusy += f'c{k}_in + '
        formulaBusy = formulaBusy[:-3] + ';\n'
        print(formulaBusy, file=self.prism_out)

        print(f'formula day = (timeOfTheDay <= 8);', file=self.prism_out)
        print(f'formula day_int = (day)?1:0;', file=self.prism_out)
        print(f'formula pick = (timeOfTheDay > 8) & (timeOfTheDay <= 14);',
              file=self.prism_out)
        print(f'formula pick_int = (pick)?1:0;',
              file=self.prism_out)
        print(f'formula night = (timeOfTheDay > 14) & (timeOfTheDay <= 24);',
              file=self.prism_out)
        print(f'formula night_int = (night)?1:0;',
              file=self.prism_out)
        print(f'formula jam = (day | pick | night) & (jamCounter > 0);',
              file=self.prism_out)  # TODO Is "jam" accessible in other module ?
        print(f'formula jam_int = (jam)?1:0;\n',
              file=self.prism_out) 
        print("formula fuelOK = (totalFuel >= 1)?1:0;\n", file=self.prism_out)
        for k in range(self.number_of_clients):
            self.client(k)

        self._taxiMove()


        
    def client(self, k):
        # TODO Random waiting time according to the size of the grid ???
        random_waiting_time = random.randrange(3, 10)

        print(
            f'global totalWaiting_c{k} : int init {random_waiting_time};', file=self.prism_out)

        print(
            f'formula waiting_c{k} = (totalWaiting_c{k} > 0) & (c{k}_in = 0);', file=self.prism_out)
        
        
        formulaRiding = f"formula riding_c{k} = (xt = xs_c{k}) & (yt = ys_c{k}) & " 
        for other_k in range(self.number_of_clients):
            if other_k != k:
                formulaRiding += f'(c{other_k}_in = 0) & '
        formulaRiding = formulaRiding[:-3] + ';'
        print(formulaRiding, file=self.prism_out) 

        # if the taxi arrived to the client0's destination or client1's destination

        print(
                f'formula reaching_c{k} = (xt = xd_c{k}) & (yt = yd_c{k}) & (c{k}_in = 1);\n', file=self.prism_out)

    def _moduleArbiter(self):
        print('\nmodule arbiter\n', file=self.prism_out)
        print(f'token : [0 .. 5] init 0;', file=self.prism_out)
        '''
            1 token for jam
            1 token for taxi position
            1 token for client0
            1 token for client1
            1 token for fuel
            1 token for day
        
            '''

        print('[updateJam] (token = 0) -> 1: (token\' = 1);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[North] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)
        print('[South] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)
        print('[East] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)
        print('[West] (token = 1) -> 1: (token\' = 2);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[client0] (token = 2) -> 1: (token\' = 3);', file=self.prism_out)
        print('[client1] (token = 3) -> 1: (token\' = 4);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[updateFuel] (token = 4) -> 1: (token\' = 5);', file=self.prism_out)

        print('', file=self.prism_out)
        print('[updateDay] (token = 5) -> 1: (token\' = 0);', file=self.prism_out)

        print('\nendmodule\n', file=self.prism_out)

    def _taxiMove(self):

        formulaLoss = 'formula loss = '  # If no more fuel
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
        # if the taxi is out of fuel
        formulaLoss += f'!(xt = xf & yt = yf) & (totalFuel = 0)'+';\n'

        formulaNorth = formulaNorth[:-3]+';'
        formulaSouth = formulaSouth[:-3]+';'
        formulaEast = formulaEast[:-3]+';'
        formulaWest = formulaWest[:-3]+';'
        # formulaLoss = formulaLoss[:-3]+';\n'
        print(formulaNorth, file=self.prism_out)
        print(formulaSouth, file=self.prism_out)
        print(formulaEast, file=self.prism_out)
        print(formulaWest, file=self.prism_out)
        print(formulaLoss, file=self.prism_out)

    def _jamUpdate(self):
        # print(f'\nmodule jamCheck\n', file=self.prism_out)
        
        print(f'[updateJam] (day & jamCounter = 0) -> 1: (jamCounter\' = jamDay);',
              file=self.prism_out)
        print(f'[updateJam] (pick & jamCounter = 0) -> 1: (jamCounter\' = jamPick);',
              file=self.prism_out)
        print(f'[updateJam] (night & jamCounter = 0) -> 1: (jamCounter\' = jamNight);',
              file=self.prism_out)
        print(f'[updateDay] true -> 1: (timeOfTheDay\' = timeOfTheDay + 1);',
              file=self.prism_out)
       
        # print('\nendmodule\n', file=self.prism_out)

    def _moduleTaxi(self):
        print('\nmodule taxi\n', file=self.prism_out)
        # position_taxi = (self.information[0][0][0], self.information[0][0][1])

        print(
            f'xt : [1..{self.height-1}] init {self.taxi[0]};', file=self.prism_out)
        print(
            f'yt : [1..{self.width-1}] init {self.taxi[1]};\n', file=self.prism_out)
        self._jamUpdate()

        print("[North] (north) -> jam_int * fuelOK: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + ((1 - jam_int) * fuelOK): (xt' = xt - 1) & (jamCounter' = 0) & (totalFuel' = totalFuel - 1);", file=self.prism_out)
        print("[South] (south) -> (jam_int * fuelOK): (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + ((1 - jam_int) * fuelOK): (xt'= xt+1) & (jamCounter' = 0)  & (totalFuel' = totalFuel-1);", file=self.prism_out)
        print("[East] (east) -> (jam_int * fuelOK): (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + ((1 - jam_int) * fuelOK): (yt'=yt+1) & (jamCounter' = 0) & (totalFuel' = totalFuel-1);", file=self.prism_out)
        print("[West] (west) -> (jam_int * fuelOK): (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + ((1 - jam_int) * fuelOK): (yt'=yt-1) & (jamCounter' = 0)  & (totalFuel' = totalFuel-1);", file=self.prism_out)
        
        print(
            f'[updateFuel] (busy = 0 & (xf = xt & yf = yt)) -> 1: (totalFuel\' = {self.fuel_level});', file=self.prism_out)

        # print("[] (win | loss) -> 1 : (end' = true);", file=self.prism_out)
        print('\nendmodule\n', file=self.prism_out)

    def _moduleClient(self):
        for k in range(self.number_of_clients):
            print(f'\nmodule client_{k}\n', file=self.prism_out)

            random_start_position, random_destination_position, random_waiting_time = self.setRandomClientAttributes()

            print(
                f'xs_c{k} : [1..{self.height-1}] init {random_start_position[0]};', file=self.prism_out)
            print(
                f'ys_c{k} : [1..{self.width-1}] init {random_start_position[1]};\n', file=self.prism_out)
            print(
                f'xd_c{k} : [1..{self.height-1}] init {random_destination_position[0]};', file=self.prism_out)
            print(
                f'yd_c{k} : [1..{self.width-1}] init {random_destination_position[1]};\n', file=self.prism_out)
            print(
                f'c{k}_in : [0..1] init 0;\n', file=self.prism_out)
            
            print(f'[client_{k}] (waiting_c{k}) -> 1: (xs_c{k}\' = xs_c{k}) & (ys_c{k}\' =  ys_c{k}) & (totalWaiting_c{k}\' = totalWaiting_c{k} - 1);', file=self.prism_out)
            print(
                f'[client_{k}] (riding_c{k}) -> 1: (xs_c{k}\' = xt) & (ys_c{k}\' = yt) & (c{k}_in\' = 1);', file=self.prism_out)

            random_start_position, random_destination_position, random_waiting_time = self.setRandomClientAttributes()

            print(f'[client_{k}] (reaching_c{k}) -> 1: (xs_c{k}\' = {random_start_position[0]}) & (ys_c{k}\' = {random_start_position[1]}) & (totalWaiting_c{k}\' = {random_waiting_time}) & (c{k}_in\' = 0);', file=self.prism_out)
            # TODO How to do ???
            print('\nendmodule\n', file=self.prism_out)
    
    def _rewards(self):
        print('rewards', file=self.prism_out)
        for k in range(self.number_of_clients): 
            print(f'(reaching_c{k}): distanceX_c{k} + distanceY_c{k};', file=self.prism_out)
        print('endrewards\n', file=self.prism_out)
  
    def setRandomClientAttributes(self):
        temp = copy.deepcopy(self.information)
        temp_probability = random.choices(
            temp, weights=[temp[i][1] for i in range(len(temp))], k=len(temp))
        random_start_position = random.choice(temp_probability)
        position_to_pop = temp.index(random_start_position)
        temp.pop(position_to_pop)
        random_start_position = random_start_position[0]
        is_airport = position_to_pop == 0
        random_destination_position = random.choice(
            temp[is_airport:])[0]  # TODO airport NOT in destination
        random_waiting_time = random.randrange(3, 10)

        return random_start_position, random_destination_position, random_waiting_time

    def createPrismFilefFromGrids(self):
        # number_of_clients = 2
        self._openOutput()
        self._initialize()
        self._moduleTaxi()
        self._moduleClient()
        self._moduleArbiter()
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

def getValue(prismFile,formula_str = "Pmax=? [F (reaching_c0|reaching_c1)]"): #TODO What to satisfy ?
	prism_program = stormpy.parse_prism_program(prismFile)
	properties = stormpy.parse_properties(formula_str, prism_program)
	model = stormpy.build_model(prism_program, properties)
	print(model)
	result = stormpy.model_checking(model, properties[0],only_initial_states=True)
	# assert result.result_for_all_states
	initial_state = model.initial_states[0]
	value = result.at(initial_state)
	del model

	gc.collect()
	return(value)
if __name__ == '__main__':
    p = createEngine("files/layouts/_10x10_0_spawn.lay")
    print(getValue(p))
    # print(getValue("files/prism/520258_15.nm"))
    pass  