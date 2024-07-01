from dijkstar import Graph, find_path
import math
import copy
import numpy as np

field_map=Graph(undirected=True)
fm_vertices=[]
fm_edges=[]
fm_shapes=[]

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
            "LF" : [0,0,1],
            "LR" : [0,1,0],
            "L" : [0,1,1],
            "FR" : [1,0,0],
            "F" : [1,0,1],
            "R" : [1,1,0],
            "O" : [1,1,1],
            }

def init_field():
    field_map.add_edge(2,4,60)
    field_map.add_edge(3,4,60)
    field_map.add_edge(5,4,60)
    field_map.add_edge(4,7,60)
    field_map.add_edge(6,7,60)
    field_map.add_edge(7,8,60)
    field_map.add_edge(7,9,60)
    
    global fm_vertices, fm_edges, fm_shapes
    fm_shapes={   2:"N", 
                    3:"E", 
                    4:"WNES",
                    5:"W", 
                    6:"E", 
                    7:"WNES",
                    8:"W", 
                    9:"S", 
                }
    
    fm_vertices={  2: (0,0),
                3: (-60,60),
                4: (0,60),
                5: (60,60),
                6: (-60,120),
                7: (0,120),
                8: (60,120),
                9: (0,180),
            }
    
    fm_edges=[  (2,4),
                (3,4),
                (4,5),
                (4,7),
                (6,7),
                (7,8),
                (7,9),
            ]

temp_map=None
temp_fm_vertices=None
temp_fm_edges=None
temp_fm_shapes=None

def get_path(source_pt, target_pt):
    global temp_map, temp_fm_vertices, temp_fm_edges, temp_fm_shapes
    temp_map=copy.deepcopy(field_map)
    temp_fm_vertices=copy.deepcopy(fm_vertices)
    temp_fm_edges=copy.deepcopy(fm_edges)
    temp_fm_shapes=copy.deepcopy(fm_shapes)

    src_idx=0
    dest_idx=1
    
    target_edge, destination_pt=closest_edge_point_on_path(target_pt)
    # add target point only if it is not on any of vertex
    if destination_pt not in temp_fm_vertices.values():
        # adding new target point between edge where the target point is
        temp_map.remove_edge(*target_edge)
        temp_map.add_edge(target_edge[0], 1, distance(destination_pt, temp_fm_vertices[target_edge[0]]))
        temp_map.add_edge(target_edge[1], 1, distance(destination_pt, temp_fm_vertices[target_edge[1]]))
        # doing the same as for edges
        temp_fm_edges.remove(target_edge)
        temp_fm_edges.extend([(target_edge[0], 1), (target_edge[1], 1)])
        # updating other entries 
        temp_fm_vertices[1]=destination_pt
        temp_fm_shapes[1]="-"

    else :
        dest_idx=list(temp_fm_vertices.keys())[list(temp_fm_vertices.values()).index(destination_pt)]

    current_edge, current_pt=closest_edge_point_on_path(source_pt)
    if current_pt!=source_pt : print("ERR: rover is not on path")
    if current_pt not in temp_fm_vertices.values():
        temp_map.remove_edge(*current_edge)    
        temp_map.add_edge(current_edge[0], 0, distance(source_pt, temp_fm_vertices[current_edge[0]]))
        temp_map.add_edge(current_edge[1], 0, distance(source_pt, temp_fm_vertices[current_edge[1]]))

        temp_fm_edges.remove(current_edge)
        temp_fm_edges.extend([(current_edge[0], 0), (current_edge[1], 0)])

        temp_fm_vertices[0]=source_pt        # - represents path not junction
        temp_fm_shapes[0]="-"

    else:
        src_idx=list(temp_fm_vertices.keys())[list(temp_fm_vertices.values()).index(current_pt)]

    return find_path(temp_map,src_idx,dest_idx).nodes

def closest_edge_point_on_path(point):
    points=[]
    dists=[]
    for edge in temp_fm_edges:
        cp=nearest_point_on_line_segment(temp_fm_vertices[edge[0]], temp_fm_vertices[edge[1]], point)
        points.append(cp)
    dists=[distance(p, point) for p in points]
    cidx=dists.index(min(dists))
    return temp_fm_edges[cidx], points[cidx]
    
def distance(p1,p2):
    return int(math.sqrt( pow((p2[0]-p1[0]), 2) + pow((p2[1]-p1[1]),2) ))

#closest point betweeen a line segment and a point
def nearest_point_on_line_segment(p, q, x):
    p=np.array(p)
    q=np.array(q)
    x=np.array(x)
    ls=np.dot((x-p),(q-p))/np.dot((q-p),(q-p))
    if ls<=0: s=p
    elif ls>1: s=q
    else: s=p+ls*(q-p)
    return tuple(s)



#  'W':-1,
#  'N':0,
#  'E':1,
#  'S':2

# current - location of rover
# target_f - coordinate of creature in field map
# orientation - W, N, E, S
def get_move_seq(source_pt, target_pt, heading): # point point num
    path = get_path(source_pt, target_pt)
    path.pop(0)
    move_seq=[]
    current_pt=source_pt
    gjunc_rot=invdir(heading)    
    for idx in path:
        direction, dist = dir_dist(current_pt, temp_fm_vertices[idx])
        rot=direction-heading 
        gjunc_rot=invdir(direction)
        if rot!=0:
            move_seq.append([gen_rotation_cmd(rot)])
        move_seq.append(["FWD", dist, g_to_ljunc(temp_fm_shapes[idx], gjunc_rot)])
        heading=direction
        current_pt=temp_fm_vertices[idx]

    return move_seq, current_pt, heading

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