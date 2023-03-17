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


TEMP_DIR = 'tempFiles'+os.sep+'prism'
try:
    os.mkdir(TEMP_DIR)
except OSError as error:
    print("{0} was not created as it already exists.".format(TEMP_DIR))
def readFromFile(layout_filename):
  
    f = open(layout_filename)
    line = f.readline().split()
    if len(line) > 4:
        raise Exception("Size mismatch : "+str(line))
    else:
        X = int(line[0])
        Y = int(line[1])
        number_of_stops = int(line[2])
        fuel_level= int(line[3])
    layout_str = []
    for i in range(X):
        layout_str.append(f.readline().strip('\n'))
        # print(layout_str)
    walls = [[layout_str[i][j] == "%" for j in range(len(layout_str[i]))] for i in range(len(layout_str))]
    stops = [[layout_str[i][j] == "." for j in range(len(layout_str[i]))] for i in range(len(layout_str))]
    fuel_station = [[layout_str[i][j] == "F" for j in range(len(layout_str[i]))] for i in range(len(layout_str))]
    airport = [[layout_str[i][j] == "A" for j in range(len(layout_str[i]))] for i in range(len(layout_str))]

    information = []
    for i in range(number_of_stops+1):
        str_information = f.readline().split()
        if len(str_information) > 3:
            raise Exception("Size mismatch : "+str(str_information))
        else:
            information.append(((int(str_information[0]),int(str_information[1])),float(str_information[2])))
            # Taxi positions, Airport position & spawn prob, Stops positions &spawn prob
    f.close()
    return (walls, stops, fuel_station, airport, information, number_of_stops, fuel_level)



def createPrismFilefFromGrids(walls, stops, fuel_station, airport, information, number_of_stops, fuel_level):
    height = len(walls)
    width = len(walls[0])

    fname = TEMP_DIR+os.sep+str(os.getpid())+f'_{number_of_stops}.nm'
    f = open(fname, 'w+')

    print('mdp\n', file=f)

    formulaLoss = 'formula loss = ' # If no more fuel

    formulaNorth = 'formula north = '
    formulaSouth = 'formula south = '
    formulaEast = 'formula east = '
    formulaWest = 'formula west = '
    print(f'int totalFuel = {fuel_level};', file=f)
    print(f'int timeOfTheDay = 0;', file=f)  #  Day = 0-8 ]10-16,18-20] Pick = 9-14 ]6-10 & 16-18] Night = 15-24 ]20-6]
    print(f'const int jamDay = 2;', file=f)  # 2
    print(f'const int jamPick = 4;', file=f)  # 4
    print(f'const int jamNight = 1;', file=f)  # 1
    print(f'int jamCounter = 0;', file=f)  # 


    # # TODO InitAction useful?0
    # print(f'const int initAction = {initAction};', file=f)
    # """
	# initAction = 0 --> any action
	# initAction = 1 --> East
	# initAction = 2 --> West
	# initAction = 3 --> North
	# initAction = 4 --> South
	# """
    # print('global initStep : bool init true;', file=f)
    # """
	# initStep is true only on the first step and in this step only allowed actions are according to the value of initAction
	# """
    for i in range(height):
        for j in range(width):
            """
            constant wi_j is 1 if there is a wall in (i,j)th coordinate
            constant hi_j is 1 if there is a hole in (i,j)th coordinate
            constant ti_j is 1 if there is a target in (i,j)th coordinate
            constant xi_j = i and yi_j = j 
            """
            print(f'const int x{i}_{j} = {i};', file=f)
            print(f'const int y{i}_{j} = {j};', file=f)
            print(f'const int w{i}_{j} = {int(walls[i][j])};', file=f)
            print(f'const int s{i}_{j} = {int(stops[i][j])};', file=f)
            print(f'const int f{i}_{j} = {int(fuel_station[i][j])};', file=f)
            print(f'const int a{i}_{j} = {int(airport[i][j])};', file=f)
            if i > 0:
                # if there is no wall in the north
                formulaNorth += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i-1}_{j} = 0) | '
            if i < height-1:
                # if there is no wall in the south
                formulaSouth += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i+1}_{j} = 0) | '
            if j < width-1:
                # if there is no wall in the east
                formulaEast += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i}_{j+1} = 0) | '
            if j > 0:
                # if there is no wall in the west
                formulaWest += f'(x{i}_{j} = xt & y{i}_{j} = yt & w{i}_{j-1} = 0) | '
           
     # if the taxi arrived to the client1's destination or client2's destination
    formulaReward = f'(xt = xd1 & yt = yd1) | (xt = xd2 & yt = yd2) | '

    # if the taxi is out of fuel
    formulaLoss = f'!(xt = xf & yt = yf) & (totalFuel = 0)'+';\n'
    # print('global end : bool init false;\n', file=f)

    formulaNorth = formulaNorth[:-3]+';\n'
    formulaSouth = formulaSouth[:-3]+';\n'
    formulaEast = formulaEast[:-3]+';\n'
    formulaWest = formulaWest[:-3]+';\n'
    formulaReward = formulaReward[:-3]+';\n'
    # formulaLoss = formulaLoss[:-3]+';\n'
    print(formulaNorth, file=f)
    print(formulaSouth, file=f)
    print(formulaEast, file=f)
    print(formulaWest, file=f)
    print(formulaReward, file=f)
    print(formulaLoss, file=f)
    

    # print(f'formula northInt = north?1:0;\n', file=f)
    # print(f'formula southInt = south?1:0;\n', file=f)
    # print(f'formula eastInt = east?1:0;\n', file=f)
    # print(f'formula westInt = west?1:0;\n', file=f)
    # print(f'formula numDirNorth = westInt + northInt + eastInt;\n', file=f)
    # print(f'formula numDirSouth = southInt + eastInt + westInt;\n', file=f)
    # print(f'formula numDirEast = northInt + southInt + eastInt;\n', file=f)
    # print(f'formula numDirWest = northInt + southInt + westInt;\n', file=f)

    print(f'formula day = (timeOfTheDay <= 8);\n', file=f)
    print(f'formula pick = ((timeOfTheDay > 8) & (timeOfTheDay <= 14));\n', file=f)
    print(f'formula night = ((timeOfTheDay > 14) & (timeOfTheDay <= 24));\n', file=f)
    print(f'[updateJam] (day) -> 1: jamCounter\' = jamDay;',file=f)
    print(f'[updateJam] (pick) -> 1: jamCounter\' = jamPick;',file=f)
    print(f'[updateJam] (night) -> 1: jamCounter\' = jamNight;',file=f)
    print(f'[updateDay] 1 -> 1: timeOfTheDay\' = timeOfTheDay + 1;',file=f)
     

    print(f'formula jam = ((day | pick | night) & jamCounter > 0);\n', file=f)

    print('\nmodule arbiter\n', file=f)
    print(f'token : [0 .. 6] init 0;',file=f)
    '''
		1 token for jam
        1 token for taxi position
		1 token for client1
		1 token for client2
		1 token for fuel
		1 token for day
	
		'''
    
    print('[updateJam] (token = 1) -> 1: (token\' = 2);',file=f)

    print('',file=f)
    print('[East] (token = 2) -> 1: (token\' = 3);',file=f)  
    print('[West] (token = 2) -> 1: (token\' = 3);',file=f)
    print('[North] (token = 2) -> 1: (token\' = 3);',file=f)
    print('[South] (token = 2) -> 1: (token\' = 3);',file=f)

    print('',file=f)
    print('[client1] (token = 3) -> 1: (token\' = 4);',file=f)
    print('[client2] (token = 4) -> 1: (token\' = 5);',file=f)

    print('',file=f)
    print('[updateFuel] (token = 5) -> 1: (token\' = 6);',file=f)

    print('',file=f)
    print('[updateDay] (token = 6) -> 1: (token\' = 0);',file=f)

    print('\nendmodule\n', file=f)



    
    print('\nmodule taxi\n', file=f)
    position_taxi = (information[0][0][0], information[0][0][1])

    print(f'xt : [1..{height-1}] init {position_taxi[0]};', file=f)
    print(f'yt : [1..{width-1}] init {position_taxi[1]};\n', file=f)

    print("[East] (east) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (yt'=yt+1) & (jamCounter' = 0) & (totalFuel' = totalFuel-1);", file=f)
    print("[West] (west) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (yt'=yt-1) & (jamCounter' = 0)  & (totalFuel' = totalFuel-1);", file=f)
    print("[North] (north) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (xt' = xt -1) & (jamCounter'= 0) & (totalFuel' = totalFuel-1);", file=f)
    print("[South] (south) -> jam: (jamCounter' = jamCounter - 1) & (totalFuel' = totalFuel-1) + !(jam): (xt'= xt+1) & (jamCounter' = 0)  & (totalFuel' = totalFuel-1);", file=f)
    print(f'[updateFuel] (xf = xt & yf = yt) -> 1: totalFuel = {fuel_level};',file=f)
    # print("[] (win | loss) -> 1 : (end' = true);", file=f)
    print('\nendmodule\n', file=f)


    print('\nmodule client1\n', file=f)
    temp = copy.deepcopy(information[2:])
    random_start_position = random.choice(temp)[0]
    temp.pop(random_start_position)
    random_destination_position = random.choice(temp)[0]

    print(f'xc1 : [1..{height-1}] init {random_start_position[0]};', file=f)
    print(f'yc1 : [1..{width-1}] init {random_start_position[1]};\n', file=f)

    # print(f'xd1 : [1..{height-1}] init {random_destination_position[0]};', file=f)
    # print(f'yd1 : [1..{width-1}] init {random_destination_position[1]};\n', file=f)

    
    print(f'int totalWaiting1 = 5;', file=f)  #TODO Random waiting time ???


    print(f'formula waiting = totalWaiting1 > 0;\n', file=f)
    print(f'formula riding = (xc1 = xt) & (yc1 = yt);\n', file=f)
    print(f'formula reaching = ({random_destination_position[0]} = xt) &({random_destination_position[1]} = yt);\n', file=f)


    print(f'[client1] (waiting) -> 1: xc1\' = xc1 & yc1\' = yc1 & totalWaiting1\' = totalWaiting1-1 ;',file=f)
    print(f'[client1] (riding) -> 1: xc1\' = xt & yc1\' = yt;',file=f)
    
    temp = copy.deepcopy(information[2:])
    random_start_position = random.choice(temp)[0]
    temp.pop(random_start_position)
    random_destination_position = random.choice(temp)[0]
    print(f'[client1] (!(waiting) & !(riding) & !(reaching)) | (reaching) -> 1:xc1={random_start_position} & yc1={random_destination_position}& totalWaiting1 = 5 ;',file=f)

    print('\nendmodule\n', file=f)


    print('\nmodule client2\n', file=f)
    temp = copy.deepcopy(information[2:])
    random_start_position = random.choice(temp)[0]
    temp.pop(random_start_position)
    random_destination_position = random.choice(temp)[0]

    print(f'xc2 : [1..{height-1}] init {random_start_position[0]};', file=f)
    print(f'yc2 : [1..{width-1}] init {random_start_position[1]};\n', file=f)

    # print(f'xd1 : [1..{height-1}] init {random_destination_position[0]};', file=f)
    # print(f'yd1 : [1..{width-1}] init {random_destination_position[1]};\n', file=f)

    
    print(f'int totalWaiting2 = 5;', file=f)  #TODO Random waiting time ???


    print(f'formula waiting = totalWaiting2 > 0;\n', file=f)
    print(f'formula riding = (xc2 = xt) & (yc2 = yt);\n', file=f)
    print(f'formula reaching = ({random_destination_position[0]} = xt) &({random_destination_position[1]} = yt);\n', file=f)


    print(f'[client2] (waiting) -> 1: xc2\' = xc2 & yc2\' = yc2 & totalWaiting1\' = totalWaiting1-1 ;',file=f)
    print(f'[client2] (riding) -> 1: xc2\' = xt & yc2\' = yt;',file=f)
    
    temp = copy.deepcopy(information[2:])
    random_start_position = random.choice(temp)[0]
    temp.pop(random_start_position)
    random_destination_position = random.choice(temp)[0]
    print(f'[client2] (!(waiting) & !(riding) & !(reaching)) | (reaching) -> 1:xc2={random_start_position} & yc2={random_destination_position}& totalWaiting1 = 5 ;',file=f)

    print('\nendmodule\n', file=f)

    # print('rewards', file=f)
    # print('[East] true : -1;', file=f)
    # print('[West] true: -1;', file=f)
    # print('[North] true: -1;', file=f)
    # print('[South] true: -1;', file=f)
    # print('(win & !end) : 100;', file=f)
    # print('(loss & !end) : -100;', file=f)
    # print('endrewards\n', file=f)

    # print('label "win" = win;', file=f)
    # print('label "loss" = loss;', file=f)
    f.close()
    return (fname)
if __name__ == '__main__':
    print(readFromFile("layouts/_10x10_0.lay"))
    pass