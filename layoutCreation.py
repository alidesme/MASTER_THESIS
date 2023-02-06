import random, os
def createLayout(number_of_layouts, height, width, directory_layout, probability=0.9):
    try:
        os.mkdir(directory_layout)
    except OSError as error:
        print("{0} was not created as it already exists.".format(directory_layout))  
    filename=directory_layout+os.sep+'_'+str(height)+'x'+str(width)+'_'
    for i in range(number_of_layouts):
        file = open(filename+str(i)+".lay","w+")
        walls = setWallsPositions(height, width, probability)
        clients, gaz_station, airport, taxi_position = setPositions(walls,probability) 
        # print(walls)
        # for ik in range(len(walls)):
        #     print(  "WALLS{0}".format(ik) , walls[ik] )
        for ik in range(len(clients)):
            print(  "CLIENTS{0}".format(ik) , clients[ik] )
        # # print(gaz_station)
        for ik in range(len(gaz_station)):
            print(  "STATION{0}".format(ik) , gaz_station[ik] )
        # # print(airport)
        for ik in range(len(airport)):
            print(  "AIRPORT{0}".format(ik) , airport[ik] )
        # print(taxi_position)
        print(  "TAXI", taxi_position )

        file.close()
def setWallsPositions(height, width, probability=0.9):
    
    city_grid = []
    for i in range(height): # Lines
        row = []  
        for j in range(width): # Columns
            random_probability = random.random()
            (is_upperLower_borders) = i == 0 or i == height-1
            is_side_borders = j == 0 or  j == width-1
            if (is_upperLower_borders) or (is_side_borders):
                row.append(True)
            elif random_probability > probability:
                row.append(True)
            else:
                row.append(False)
        city_grid.append(row)
    return city_grid


def setPositions(walls, probability=0.9):
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
    gaz_station = new_func(walls, height, width, gaz_station, clients)[0]
    airport = new_func(walls, height, width, airport, gaz_station, clients)[0]
    taxi = new_func(walls, height, width, taxi, airport, gaz_station, clients)[1]
    # airport_line = random.randint(0, height-1)
    # airport_column = random.randint(0, width-1)
    # is_available_for_airport = is_available_for_station and gaz_station[airport_line][airport_column]
    # while not is_available_for_airport:
    #     airport_line = random.randint(0, height-1)
    #     airport_column = random.randint(0, width-1)
    #     is_available_for_airport = is_available_for_station and gaz_station[airport_line][airport_column]
    # if is_available_for_airport:
    #     airport[airport_line][airport_column] = True


    return clients, gaz_station, airport, taxi

def new_func(walls, height, width, position_to_change, *elem):
    # line = random.randint(0, height-1)
    # column = random.randint(0, width-1)
    is_available = False
    while not is_available:
        line = random.randint(0, height-1)
        column = random.randint(0, width-1)
        i = 0
        is_available = not walls[line][column] and not elem[i][line][column]

        while i < len(elem)-1 and is_available:
            is_available = not walls[line][column] and not elem[i+1][line][column]
            i+=1

        if is_available :
            position_to_change[line][column] = True
    
# is_available = False
#     i=0
#     while not is_available:
#         line = random.randint(0, height-1)
#         column = random.randint(0, width-1)
#         is_available = not walls[line][column] and not elem1[line][column]
#         # print(is_available)
#         if (len(elem2) > 0):
#             is_available = not walls[line][column] and not elem1[line][column]and not elem2[line][column] 
#             if (len(elem3)>0):
#                 is_available = not walls[line][column] and not elem1[line][column]and not elem2[line][column]and not elem3[line][column] 

#         if is_available :
#             position_to_change[line][column] = True
    



    # for i in range(len(elem)):
    #     is_available = not walls[line][column] and not elem[i][line][column]
    # while not is_available:
    #     line = random.randint(0, height-1)
    #     column = random.randint(0, width-1)
    #     ok = True
    #     for i in range(len(elem)):
    #         ok = ok and not elem[i][line][column]
    #     is_available = not walls[line][column] and ok
    # if is_available:
    #     position_to_change[line][column] = True
    return position_to_change, (line,column)
if __name__ == '__main__':
	createLayout(1,5,7,"test",probability=0.9)
	pass
