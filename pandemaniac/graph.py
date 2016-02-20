import json
import random
import sim


def average(lst):
	return float(sum(lst))/len(lst)

class NetworkNode(object):
	"""docstring for NetworkNode"""
	def __init__(self):
		super(NetworkNode, self).__init__()
		self.neighbor_set = set()

	def degree(self):
		return len(self.neighbor_set)

	def triple_count(self):
		return (self.degree() * (self.degree() - 1))/2

	def triangle_count(self):
		triangle_count = 0
		for adj1 in self.neighbor_set:
			for adj2 in self.neighbor_set:
				if adj1 == adj2:
					continue
				if adj1 in adj2.neighbor_set:
					triangle_count += 1
		# Divide, because of double counting
		triangle_count /= 2
		return triangle_count

	def clustering_coefficient(self):
		if self.triple_count() == 0:
			return 0
		return float(self.triangle_count())/self.triple_count()

	def get_distance_dict(self):
		distance_dict = {self: 0}
		current_bfs_depth = 0
		current_node_set = set([self])

		while current_node_set:

			for node in current_node_set:
				distance_dict[node] = current_bfs_depth

			next_node_set = set()
			for depth_node in current_node_set:
				for adj_node in depth_node.neighbor_set:
					if adj_node not in distance_dict:
						next_node_set.add(adj_node)

			current_node_set = next_node_set
			current_bfs_depth += 1

		return distance_dict


class Network(object):
	"""docstring for graph"""
	def __init__(self, arg):
		super(Network, self).__init__()

		# The dict interpreted from a JSON string
		self.name_dict = arg

		# A dict mapping "1", "2", "3" and so on to Node objects
		self.node_dict = dict()
		self.node_set = set()

		for vertex_name in self.name_dict:
			self.node_dict[vertex_name] = NetworkNode()
			self.node_set.add(self.node_dict[vertex_name])

		for vertex_name in self.name_dict:
			node1 = self.node_dict[vertex_name]

			for adjacent_name in self.name_dict[vertex_name]:
				if adjacent_name in self.node_dict:
					node2 = self.node_dict[adjacent_name]
					node1.neighbor_set.add(node2)
					node2.neighbor_set.add(node1)


	def get_node(self, name):
		return self.node_dict[name]

	def average_clustering_coefficient(self):
		return average(
			[vertex.clustering_coefficient() for vertex in self.node_set])

	def overall_clustering_coefficient(self):
		triangle_counts = [vertex.triangle_count() for vertex in self.node_set]
		triple_counts = [vertex.triple_count() for vertex in self.node_set]
		total_triangle_count = float(sum(triangle_counts))
		total_triple_count = float(sum(triple_counts))
		return total_triangle_count/total_triple_count



	def diameter(self):

		max_distances = list()
		for node1 in self.node_set:
			distances = node1.get_distance_dict()
			if len(distances) < len(self.node_set):

				assert False
			max_distances.append(max([distances[n] for n in distances]))
		return max(max_distances)



	def average_distance(self):
		distance_list = []
		for node1 in self.node_set:
			distances = node1.get_distance_dict()
			distance_list.extend(
				[distances[node2] for node2 in distances if node2 != node1])
		return average(distance_list)


class Player(object):
	"""The Player class is an abstract class for strategies for playing."""
	def __init__(self):
		super(Player, self).__init__()


		self.filename = None
		self.graphname = None

		self.num_players = None
		self.num_seeds = None
		self.graph_id = None
		self.graph = None


	def set_filename(self, filename):
		""" This method allows us to initialize a player with a certain graph
		in the graph_files directory"""

		self.filename = filename

		self.graphname = filename[len("graph_files/"):]


		num_list = map(int, self.graphname.split(".")[:3])
		self.num_players = num_list[0]
		self.num_seeds = num_list[1]
		self.graph_id = num_list[2]

		file = open(filename)

		self.graph = Network(json.loads(file.read()))

		file.close()


	def give_50_output_to_file(self):
		""" This method causes the player to output its selections to an
		ouput file, for 50 rounds of the game."""


		file = open("output_files/" + self.graphname + ".output" , "w+")

		for i in range(50):
			for node in self.give_output_list():
				file.write(node + "\n")

		file.close()



class RandomPlayer(Player):
	"""docstring for RandomPlayer"""
	def __init__(self):
		Player.__init__(self)


	def give_output_list(self):
		""" THis returns a list of the selected nodes. The random player
		chooses these randomly."""

		# Create a set of selections.
		selections = set()

		# Randomly add nodes until we have the right number of seeds
		while len(selections) < self.num_seeds:
			selections.add(random.choice(list(self.graph.node_dict.keys())))

		return list(selections)

class HighDegreePlayer(Player):

	def __init__(self):
		Player.__init__(self)

	def give_output_list(self):

		nodes = list(self.graph.node_dict.keys())

		nodes.sort(key=lambda x : self.graph.node_dict[x].degree(), reverse=True)

		return nodes[:self.num_seeds]

class TwinAttackPlayer(Player):

	def __init__(self):
		Player.__init__(self)

	def give_output_list(self):

		nodes = list(self.graph.node_dict.keys())

		nodes.sort(key=lambda x : self.graph.node_dict[x].degree(), reverse=True)

		selections = set()

		for name in nodes[5:]:
			if len(selections) == self.num_seeds:
				break
			adjacents = self.graph.name_dict[name]
			for adj_name in adjacents[:2]:
				selections.add(adj_name)



		return list(selections)




def erdos_renyi_dict(n, p):

	graphdict = {str(i) : [] for i in range(n)}

	for i in range(n):
		for j in range(i):
			if random.random() < p:
				graphdict[str(i)].append(str(j))
				graphdict[str(j)].append(str(i))

	return graphdict


def play(filename, playerlist):

	graphname = filename[len("graph_files/"):]


	num_list = map(int, graphname.split(".")[:3])
	num_players = num_list[0]

	assert num_players == len(playerlist)

	num_seeds = num_list[1]
	graph_id = num_list[2]



	file = open(filename)

	graph = json.loads(file.read())

	file.close()

	for player in playerlist:
		#print player
		player.set_filename(filename)

	nodes = {}

	for i, player in enumerate(playerlist):
		nodes["strategy" + str(i)] = player.give_output_list()


	result = sim.run(graph, nodes)

	return result

def play_iterate(iterations, num_nodes, n, p, playerlist):

	total_dict = {}
	for i in range(len(playerlist)):
		total_dict["strategy" + str(i)] = 0

	for i in range(iterations):
		result = play(num_nodes, n, p, playerlist)
		for strategy in result:
			total_dict[strategy] += result[strategy]

	print total_dict


def main():

	#play_iterate(1, 5, 100, 0.05, [HighDegreePlayer(), TwinAttackPlayer()])

	print play("graph_files/2.5.1.json", [TwinAttackPlayer(), HighDegreePlayer()])


if __name__ == '__main__':
	main()
