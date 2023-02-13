"""
Author      : DESMET Aline 
Matricule   : 000474868 (MA2-INFO)
Description : Generate prism file
"""

def readFromFile(layout_filename):
  
    f = open(layout_filename)
    line = f.readline().split()
    if len(line) > 4:
        raise Exception("Size mismatch : "+str(line))
    else:
        X = int(line[0])
        Y = int(line[1])
        number_of_clients = int(line[2])
        fuel_level= int(line[3])
    layout_str = []
    for i in range(X):
        layout_str.append(f.readline().strip('\n'))
    walls = [[layout_str[i][j] == "%" for j in range(len(layout_str[i]))] for i in range(len(layout_str))]
    clients = [[layout_str[i][j] == "." for j in range(len(layout_str[i]))] for i in range(len(layout_str))]
    fuel_station = [[layout_str[i][j] == "F" for j in range(len(layout_str[i]))] for i in range(len(layout_str))]
    airport = [[layout_str[i][j] == "A" for j in range(len(layout_str[i]))] for i in range(len(layout_str))]

    
    f.close()
    return (walls, clients, fuel_station, airport, number_of_clients, fuel_level)
if __name__ == '__main__':
    print(readFromFile("simplified_layouts/_10x10_0.lay"))
    pass