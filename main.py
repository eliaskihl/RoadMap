import folium
import pickle
import pandas as pd
import os 
import numpy as np
from geopy.distance import geodesic
import time
import heapq
# from scipy.spatial import KDTree
class Node:
    def __init__(self, lat, long, name, country, population, map_instance):
        self.lat = lat
        self.long = long
        self.name = name
        self.country = country
        self.population = population
        self.map_instance = map_instance  # Corrected attribute
        self.neighbors = []
        self.neighbors_distances = {}

    def check_if_same_dir(src,node,nodes):
        pass
        # ex:
        # Osmanyie 36,25
        # Torpankelle 36,37
        # Erzin 36,36
        # Kuzunchuli 36,36
        # Yesilköy 36,36
        """
        om 2 är neråt välj 2 uppåt?
        om 2 är till vänster välj två till höger
        """
        up_down,left_right = get_direction()
        if up_down == "south":
            south += 1
        elif up_down == "north":
            north += 1
        if left_right == "west":
            west += 1
        elif left_right == "east":
            east += 1


    def find_neighbor(self, all_nodes,num_neighbors=7):
        file_path = f"./neighbors/{self.country}/"
        file_name = f"neighbor_of_{self.name}"
        full_path = file_path + file_name
        # Try loading neighbors
        try:
            with open(full_path, 'rb') as file:
                neighbor_names = pickle.load(file)  # Load names of neighbors
                self.neighbors = [all_nodes[name] for name in neighbor_names if name in all_nodes]  # Convert names to objects
                for node in self.neighbors:
                    self.neighbors_distances = geodesic((self.lat, self.long), (node.lat, node.long)).km
                print(f"Neighbors for {self.name} loaded from file.")
                return
        except (FileNotFoundError,EOFError):
            print(f"No saved neighbors for {self.name}, needs to be calculated")
        # Find local neighbors
        distances = []
        
        #twice = []
        direction_buckets = {
            "north": [],
            "south": [],
            "east": [],
            "west": []
        }
        for name, node in all_nodes.items():
            if name == self.name:
                continue  # Skip itself
            # Compute direction
            hor, ver = get_direction(self,node)
            
            # Compute geodesic distance
            dist = geodesic((self.lat, self.long), (node.lat, node.long)).km
            direction_buckets[hor].append((dist, node))
            direction_buckets[ver].append((dist, node))

        # pick 2 closest nodes from 
        closest_nodes = []
        for keys,_ in direction_buckets.items():   
        
            closest_nodes.append(heapq.nsmallest(int(num_neighbors/2), direction_buckets[keys], key=lambda x: x[0]))

        closest_nodes = [lst for lst in closest_nodes if lst]

        # print(closest_nodes)
        # Extract only the node objects (ignoring the distance value)
        self.neighbors = [node[-1] for node in closest_nodes]
        self.neighbors = [node for _, node in self.neighbors]

        # Save neightbors
        neighbor_names = [node.name for node in self.neighbors]  # Store only names

        if not os.path.exists(file_path):
            os.mkdir(file_path)
        with open(full_path, 'wb') as file:
            pickle.dump(neighbor_names, file) 

        
            
        # of all nodes, find the cloest nodes in each direction, if there is one in threshold value distance else, no neighbor, every node must have atleast one neighbor
    def print_node(self):
        radius = max(3, min(self.population / 500000, 15))  # Scale population to reasonable range
        
        folium.CircleMarker(
            location=[self.lat, self.long],
            radius=radius,  # Set radius based on population
            color="blue",   # Circle color
            fill=True,      # Fill the circle
            fill_color="blue",  # Fill color
            fill_opacity=1.0,   # Fill opacity
            tooltip=f"{self.name} - Population: {self.population} - Coords: ({self.long},{self.lat})"  # Tooltip with city name and population
        ).add_to(self.map_instance.m)

class Map:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long
        self.m = folium.Map(
            location=[self.lat, self.long], zoom_start=6,
            tiles='https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
            attr="OpenStreetMap"
        )

    def save_map(self):
        self.m.save("map.html")  # Ensure map is saved
        print("Map saved as 'map.html'.")
        #webbrowser.open("file://" + "map.html")

    def load_cities(self):
        df = pd.read_csv(os.path.abspath("worldcities.csv"))
        df = df.drop(columns=["city_ascii", "iso2", "iso3", "admin_name", "capital", "id"])
        # Drop cities with too little population
        # df = df[df["population"] > 50000]
        df = df[df["country"].isin(["Turkey","Armenia","Azerbaijan"])]
        # Sort by country
        df = df.sort_values('country')
        # df = df.sample(frac=0.05, random_state=1)  # frac=0.5 to sample 50%
        print("Length of df:", len(df))

        return df

class Line:
    def __init__(self,node1,node2,map_instance,color):
        self.map_instance = map_instance
        self.node1 = node1
        self.node2 = node2
        self.color= color
    def draw_line(self):
        folium.PolyLine(
            locations=[[self.node1.lat, self.node1.long], [self.node2.lat, self.node2.long]],  # Start and end coordinates
            color=self.color,  # Line color
            weight=3,  # Thickness
            opacity=1
        ).add_to(self.map_instance.m)

class Route:
    def __init__(self,start,end,name):
        self.start = start
        self.end = end
        self.name = name

def get_direction(src,dest):
        up_down = None
        left_right = None
        if src.lat < dest.lat: # neighbor is east
            left_right = "east"
        else: # then must be west
            left_right = "west"

        if src.long < dest.long:
            up_down = "north"
        else:
            up_down = "south"
        return left_right,up_down 


def djikstras(graph,node):
    """
    for each vertex v in Graph.Vertices:
 4          dist[v] ← INFINITY
 5          prev[v] ← UNDEFINED
 6          add v to Q
 7      dist[source] ← 0
 8     
 9      while Q is not empty:
10          u ← vertex in Q with minimum dist[u]
11          remove u from Q
12         
13          for each neighbor v of u still in Q:
14              alt ← dist[u] + Graph.Edges(u, v)
15              if alt < dist[v]:
16                  dist[v] ← alt
17                  prev[v] ← u
18
19      return dist[], prev[
    """
    pass
        

def buildRoad(start,end,map,visited=None):
    if visited == None:
        visited = set()
    if start in visited:
        print("Infinite recurision at:",start.name)
        return
    print(visited)
    visited.add(start)
    # TODO: Fix Max recursion reached problem
    if end == start:  # Avoid infinite recursion
        print("Arrived")
        return
    distances = []
    print("We are at:", start.name)
    for node in start.neighbors:
        if node not in visited:  # Only consider unvisited nodes
            dist = geodesic((node.lat, node.long), (end.lat, end.long)).km
            print("name:",node.name,"dist:",dist)
            distances.append((dist, node))
    if not distances:  # No valid neighbors left
        print("No more unvisited neighbors, stopping pathfinding.")
        return
    closest_node = min(distances, key=lambda x: x[0])[1]  # Min finds the closest valid node
    
    # Print line
    line = Line(start,closest_node,map,color="green")
    line.draw_line()
    buildRoad(closest_node,end,map,visited)

def create_lines(all_nodes):
   
    for name,node in all_nodes.items():
        node.find_neighbor(all_nodes)
        for neighbor in node.neighbors:
            line = Line(node,neighbor,node.map_instance,color="red")
            line.draw_line()   
    



def gen_nodes(map_inst):
    nodes = {}
    df = map_inst.load_cities()
    for row in df.itertuples(index=False):
        node = Node(
            lat=row.lat,
            long=row.lng,
            name=row.city,
            country=row.country,
            population=row.population,
            map_instance=map_inst
            
        )
        
        # Call print_node() method for this specific node instance
        node.print_node()
        nodes[row.city] = node
    return nodes



def find_city(city,nodes):
    for name,node in nodes.items():
        if name == city:
            return node
    
    raise Exception("No nodes found with that name.")


def main():
    # TODO:
    ## Optimize by only generating necessary cities for the countries the route passes.
    # Create a map instance
    
    
    start = time.time()
    map1 = Map(13.0,55.0)  
    # Create and add a node
    nodes = gen_nodes(map1)

    node1 = find_city("Osmaniye",nodes)
    node2 = find_city("Baku",nodes)

    create_lines(nodes)
    
    buildRoad(node1,node2,map1)
    # node1 = Node(45.3288, -121.6625, "Mt. Hood", 100000, map1)
    # node2 = Node(45.5, -122.0, "Small City", 50000, map1)
    end = time.time()

    print("Total runtime:",end-start)
    

    
    # line = Line(node1,node2,map1)
    # line.draw_line()
    # print(nodes)
    # Save the final map with all markers
    map1.save_map()
    

if __name__ == "__main__":
    main()
