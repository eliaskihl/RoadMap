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
       
                    
    def find_neighbor(self, all_nodes,num_neighbors=4):
        file_path = f"./neighbors/{self.country}/"
        file_name = f"neighbor_of_{self.name}"
        full_path = file_path + file_name
        # Try loading neighbors
        try:
            with open(full_path, 'rb') as file:
                neighbor_names = pickle.load(file)  # Load names of neighbors
                self.neighbors = [all_nodes[name] for name in neighbor_names if name in all_nodes]  # Convert names to objects
                print(f"Neighbors for {self.name} loaded from file.")
                return
        except FileNotFoundError:
            print(f"No saved neighbors for {self.name}, needs to be calculated")
        # Find local neighbors
        distances = []
        
        #twice = []
        for name, node in all_nodes.items():
            if name == self.name:
                continue  # Skip itself
            # Compute geodesic distance
            dist = geodesic((self.lat, self.long), (node.lat, node.long)).km
            distances.append((dist, node))

        closest_nodes = heapq.nsmallest(num_neighbors, distances, key=lambda x: x[0])

        # Extract only the node objects (ignoring the distance value)
        self.neighbors = [node for _, node in closest_nodes]
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
        df = df[df["country"].isin(["Norway","Finland","Sweden","Turkey","Armenia","Azerbaijan","Georgia"])]
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


    
# def Dijkstra(self,start,end):
    # distances = {}
    # prev = {}
    # q = []
    # for node in (self.nodes):
    #     if node == self.start:
    #         distances[node] = 0
    #     distances[node] = np.inf
    #     prev[node] = np.nan
    #     q.append(node)
    # while q:
    #     # Get min distance
    #     u = min(distances,key = distances.get()) # Get node with shortest distance
    #     q.pop(q.index(u)) # Remove from list
    #     for neighbor in self.neigh

def buildRoad(start,end,map):
    # end.lat 
    # end.long
    # take node which shortest abs distance to end
    # call that node using buildRoad
    # recursive
    if end == start:  # Avoid infinite recursion
        print("Arrived")
        return
    distances = []
    print("We are at:", start.name)
    for node in start.neighbors:
        dist = geodesic((node.lat, node.long), (end.lat, end.long)).km
        distances.append((dist, node))
  
    closest_node = heapq.nsmallest(1, distances, key=lambda x: x[0])[0][1] # Takes the node part of the returning tuple [(dist,node)]
    
    # Print line
    line = Line(start,closest_node,map,color="green")
    line.draw_line()
    buildRoad(closest_node,end,map)

def create_lines(all_nodes):
    start = time.time()

    for name,node in all_nodes.items():
        node.find_neighbor(all_nodes)
        for neighbor in node.neighbors:
            line = Line(node,neighbor,node.map_instance,color="red")
            line.draw_line()   
    end = time.time()
    print("Runtime:",end - start)



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

    # node1 = find_city("Malmö",nodes)
    # node2 = find_city("Stockholm",nodes)

    create_lines(nodes)
    
    # buildRoad(node1,node2,map1)
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
