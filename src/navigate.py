from dijkstar import Graph, find_path
import math
import copy

field_map=Graph(undirected=True)
field_map_vertices=None
field_map_lines=None
gjunctions={"WNES"  :[0,0,0,0],
            "WNE"   :[0,0,0,1],
            "WNS"   :[0,0,1,0],
            "WN"    :[0,0,1,1],
            "WES"   :[0,1,0,0],
            "WE"    :[0,1,0,1],
            "WS"    :[0,1,1,0],
            "W"     :[0,1,1,1],
            "NES"   :[1,0,0,0],
            "NE"    :[1,0,0,1],
            "NS"    :[1,0,1,0],
            "N"     :[1,0,1,1],
            "ES"    :[1,1,0,0],
            "E"     :[1,1,0,1],
            "S"     :[1,1,1,0],
            "O"     :[1,1,1,1],
            }

ljunctions={"LFR" : [0,0,0],
            " LF" : [0,0,1],
            " LR" : [0,1,0],
            "  L" : [0,1,1],
            " FR" : [1,0,0],
            "  F" : [1,0,1],
            "  R" : [1,1,0],
            "  O" : [1,1,1],
            }
def init_field():
    field_map.add_edge(2,4,60)
    field_map.add_edge(3,4,60)
    field_map.add_edge(5,4,60)
    field_map.add_edge(4,7,60)
    field_map.add_edge(6,7,60)
    field_map.add_edge(7,8,60)
    field_map.add_edge(7,9,60)
    
    global field_map_vertices, field_map_lines
    field_map_vertices={2:["N", (0,0)],
                        3:["E", (-60,60)],
                        4:["WNES", (0,60)],
                        5:["W", (60,60)],
                        6:["E", (-60,120)],
                        7:["WNES", (0,120)],
                        8:["W", (60,120)],
                        9:["S", (0,180)]
                        }
    field_map_lines=[(2,4),
                     (3,4),
                     (4,5),
                     (4,7),
                     (6,7),
                     (7,8),
                     (7,9)
                    ]

def get_path(source_pt, target_pt):
    temp_map=copy.deepcopy(field_map)
    temp_fm_vertices=copy.deepcopy(field_map_vertices)

    edge, destination_pt=closest_point_on_path(target_pt)
    cur_edge, curp=closest_point_on_path(source_pt)
    if not curp==source_pt : print("err: rover is not on path")

    temp_map.remove_edge(*edge)
    temp_map.remove_edge(*cur_edge)

    temp_map.add_edge(edge[0], 1, distance(destination_pt, field_map_vertices[edge[0]][1]))
    temp_map.add_edge(edge[1], 1, distance(destination_pt, field_map_vertices[edge[1]][1]))

    temp_map.add_edge(cur_edge[0], 0, distance(source_pt, field_map_vertices[cur_edge[0]][1]))
    temp_map.add_edge(cur_edge[1], 0, distance(source_pt, field_map_vertices[cur_edge[1]][1]))

    #print(destination_pt, edge,field_map_vertices[edge[0]][1] , distance(destination_pt, field_map_vertices[edge[0]][1]))
    
    temp_fm_vertices[0]=["-", source_pt]        # - represents path not junction
    temp_fm_vertices[1]=["-", destination_pt]

    return find_path(temp_map,0,1).nodes, temp_fm_vertices

def closest_point_on_path(point):
    points=[]
    dists=[]
    for line in field_map_lines:
        cp=p4(field_map_vertices[line[0]][1], field_map_vertices[line[1]][1], point)
        points.append(cp)
    #print(points)
    dists=[distance(p, point) for p in points]
    cidx=dists.index(min(dists))
    return field_map_lines[cidx], points[cidx]
    
# returns the closest distance to line and point
def find_lp_distance(l1,l2,p): # x1,y1  x2,y2, x0,y0
    return int(abs( (l2[1]-l1[1])*p[0] - (l2[0]-l1[0])*p[1] + l2[0]*l1[1] - l2[1]*l1[0] ) / math.sqrt( (l2[1]-l1[1])**2 + (l2[0]-l1[0])**2 ))

def distance(p1,p2):
    return int(math.sqrt( pow((p2[0]-p1[0]), 2) + pow((p2[1]-p1[1]),2) ))

def p4(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    dx, dy = x2-x1, y2-y1
    det = dx*dx + dy*dy
    a = (dy*(y3-y1)+dx*(x3-x1))/det
    return x1+a*dx, y1+a*dy


#  'W':-1,
#  'N':0,
#  'E':1,
#  'S':2

# current - location of rover
# target_f - coordinate of creature in field map
# orientation - W, N, E, S
def get_move_seq(source_pt, target_pt, heading): # point point num
    path, temp_fm_vertices = get_path(source_pt, target_pt)
    path.pop(0)
    move_seq=[]
    current_pt=source_pt
    gjunc_rot=invdir(heading)    
    for idx in path:
        direction, dist = dir_dist(current_pt, temp_fm_vertices[idx][1])
        rot=direction-heading 
        gjunc_rot=invdir(direction)
        if rot!=0:
            move_seq.append([gen_rotation_cmd(rot)])
        move_seq.append(["FWD", dist, g_to_ljunc(temp_fm_vertices[idx][0], gjunc_rot)])
        heading=direction
        current_pt=temp_fm_vertices[idx][1]

    return move_seq

def dir_dist(pinit, pfinal):
    p=(pfinal[0]-pinit[0], pfinal[1]-pinit[1])
    if p==(0,0) or (p[0]>0 and p[1]>0):
        return 0, 0
    if not p[0]==0:
        return (-1 if p[0]<0 else 1) , abs(p[0])
    else:
        return (2 if p[1]<0 else 0) , abs(p[1])
    
def gen_rotation_cmd(rot):
    rot=math.remainder(rot,4) # Difference between x and the closest integer multiple of y.
    if rot==0:
        return ""
    if abs(rot)==2:
        return "UTRN"
    if rot<0:
        return "LFT" 
    else :
        return "RGT"
    
def invdir(direction):
    return -1*direction

def g_to_ljunc(gjunc, rot):
    if gjunc=="-":
        return "-"
    gjunc=gjunctions[gjunc]
    rotated_gjunc=gjunc[-1*rot : ] + gjunc[ : -1*rot]
    return list(ljunctions.keys())[list(ljunctions.values()).index(rotated_gjunc[:3])]