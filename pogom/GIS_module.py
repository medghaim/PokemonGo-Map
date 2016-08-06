from s2sphere import *
from math import radians, cos, sin, asin, sqrt

def get_fort_path_cells(latlng):
    """For fort visibility, Niantic uses 10 forward, and 10 backward
    steps on a Hilbert curve, at level 15. This function returns those level 15 cells ID's.
    Returns:
     - A list containing ID's of the twenty lvl15 s2cells containing forts
     that a player will see at 1 pulse/heartbeat/step.
    """
    WALK_LEVEL = 15 #level 15 s2cell
    PATH_LENGTH = 10 #10 forward, 10 backward
    #Starting cell is a location - a level 30 cell (15 parent calls crawls up to level 15)
    start_cell = CellId().from_lat_lng(latlng).parent(WALK_LEVEL)

    walk_path = [Cell(start_cell)]
    
    next_cell = start_cell.next()
    prev_cell = start_cell.prev()
    for i in range(PATH_LENGTH):
        walk_path.append(Cell(next_cell)) # cell obj
        walk_path.append(Cell(prev_cell)) # cell obj
        next_cell = next_cell.next()
        prev_cell = prev_cell.prev()
    return walk_path

def get_location_cell(latlng):
    return Cell(CellId().from_lat_lng(latlng).parent(15))

def get_fort_path_ids(latlng):
    return sorted([c.id() for c in (get_fort_path_cells(latlng))]) #sorted cellid's = sorted .pos()'s

def get_hilbert_range(latlng):
    """ Returns the start and end points of a 10/10 hilbert walk (see get_fort_walkpath)
    useful for testing if the level30 s2cell (ie, pokestop/gym latlng)
    falls within range of a 10 front/back hilbert walk 
     - ie, path[0] <= fort.latlng <= path[1]
     - Useful for telling us if we've already checked a pokestop!
    """
    path = get_fort_path_ids(latlng)
    return [path[0], path[-1]] #return first and last cell ids

def fort_already_seen(latlng, walk_ranges):
    """ Returns true if a fort's latlng (ie, lvl 30 cell) falls between a fort walkpath"""
    cell = Cell.from_lat_lng(latlng) #lvl 30 (smallest) cell
    for fort_range in walk_ranges:
        if fort_range[0].pos() <= cell.id().pos() <= fort_range[1].pos():
            return True
    return False


def get_new_coords(init_loc, distance, bearing):
    """ Given an initial lat/lng, a distance(in kms), and a bearing (degrees),
    this will calculate the resulting lat/lng coordinates.
    """ 
    R = 6378.137 #km radius of the earth
    bearing = math.radians(bearing)

    init_coords = [math.radians(init_loc[0]), math.radians(init_loc[1])] # convert lat/lng to radians

    new_lat = math.asin( math.sin(init_coords[0])*math.cos(distance/R) +
            math.cos(init_coords[0])*math.sin(distance/R)*math.cos(bearing))

    new_lon = init_coords[1] + math.atan2(math.sin(bearing)*math.sin(distance/R)*math.cos(init_coords[0]),
            math.cos(distance/R)-math.sin(init_coords[0])*math.sin(new_lat))

    return [math.degrees(new_lat), math.degrees(new_lon)]

def _haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6378.137 * c
    return km*1000


def in_range(step, fort):
    """Calculates whether or not a fort is within range of a step location"""
    dist = _haversine(  step.lat().degrees, step.lng().degrees,
                        fort.lat().degrees, fort.lng().degrees )
    #dist = _haversine(step.lat(), step.lng(), fort.lat(), fort.lng())
    print(dist)
    return dist <= 70