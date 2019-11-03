from collections import deque, namedtuple
from datetime import datetime

# we'll use infinity as a default distance to nodes.
inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')
NUM_List = ['50', '16', '80', '48', '32']
#NUM_List = ['118', '134', '148', '12', '164']

def make_edge(start, end, cost=1):
  return Edge(start, end, cost)

class Graph:
    def __init__(self, edges):
        # let's check that the data is right
        wrong_edges = [i for i in edges if len(i) not in [2, 3]]
        if wrong_edges:
            raise ValueError('Wrong edges data: {}'.format(wrong_edges))

        self.edges = [make_edge(*edge) for edge in edges]

    @property
    def vertices(self):
        return set(
            sum(
                ([edge.start, edge.end] for edge in self.edges), []
            )
        )

    def get_node_pairs(self, n1, n2, both_ends=True):
        if both_ends:
            node_pairs = [[n1, n2], [n2, n1]]
        else:
            node_pairs = [[n1, n2]]
        return node_pairs

    def remove_edge(self, n1, n2, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        edges = self.edges[:]
        for edge in edges:
            if [edge.start, edge.end] in node_pairs:
                self.edges.remove(edge)

    def add_edge(self, n1, n2, cost=1, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        for edge in self.edges:
            if [edge.start, edge.end] in node_pairs:
                return ValueError('Edge {} {} already exists'.format(n1, n2))

        self.edges.append(Edge(start=n1, end=n2, cost=cost))
        if both_ends:
            self.edges.append(Edge(start=n2, end=n1, cost=cost))

    @property
    def neighbours(self):
        neighbours = {vertex: set() for vertex in self.vertices}
        for edge in self.edges:
            neighbours[edge.start].add((edge.end, edge.cost))

        return neighbours

    def dijkstra(self, source, dest):
        assert source in self.vertices, 'Such source node doesn\'t exist'
        distances = {vertex: inf for vertex in self.vertices}
        previous_vertices = {
            vertex: None for vertex in self.vertices
        }
        distances[source] = 0
        vertices = self.vertices.copy()

        while vertices:
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])
            vertices.remove(current_vertex)
            if distances[current_vertex] == inf:
                break
            for neighbour, cost in self.neighbours[current_vertex]:
                alternative_route = distances[current_vertex] + cost
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        return path

def makePath(start, end):
	global NUM_List
	if(start not in NUM_List or end not in NUM_List):
		return None
	else:
		t = list(graph.dijkstra(start, end))
		#print(t[0], t[1])
		for i in range(0, len(Angle_graph), 1):
			if((Angle_graph[i][0] == t[0]) and (Angle_graph[i][1] == t[1])):
				return (t[1], Angle_graph[i][2])
'''
graph = Graph([
	("a", "b", 1), 
	("b", "a", 1), ("b", "c", 1), ("b", "f", 1),
	("c", "b", 1), ("c", "d", 1),
	("d", "c", 1), ("d", "e", 1),
	("e", "d", 1), ("e", "f", 1),
	("f", "b", 1), ("f", "e", 1)
])
Angle_graph = [["a", "b", 90], 
	["b", "a", 180], ["b", "c", -90], ["b", "f", 0],
	["c", "b", 120], ["c", "d", 180],
	["d", "c", -30], ["d", "e", -120],
	["e", "d", 120], ["e", "f", 80],
	["f", "b", 170], ["f", "e", 10]
]
'''
'''
graph = Graph([
	("118", "134", 1), ("134", "118", 1),
	("12", "134", 1), ("134", "12", 1),
	("12", "148", 1), ("148", "12", 1),
	("164", "148", 1), ("148", "164", 1)
])
	

Angle_graph = [
	("118", "134", 0), ("134", "118",180),
	("12", "134", -90), ("134", "12", 90),
	("12", "148", 90), ("148", "12", -90),
	("164", "148", 0), ("148", "164", 180)
]
'''
graph = Graph([
	("50", "16", 1),
	("16", "80", 1), ("16", "50", 1), 
	("80", "16", 1), ("80", "48", 1),
	("48", "32", 1), ("48", "80", 1),
	("32", "48", 1)
])
	

Angle_graph = [
	("50", "16", 90),
	("16", "80", 180), ("16", "50", -90),
	("80", "16", 0), ("80", "48", -90),
	("48", "32", -90), ("48", "80", 90),
	("32", "48", 90)
]

#makePath("b", "e")
