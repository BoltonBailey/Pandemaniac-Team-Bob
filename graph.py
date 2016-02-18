import json
import matplotlib.pyplot as plt

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

		for vertex_name in arg:
			self.node_dict[vertex_name] = NetworkNode()
			self.node_set.add(self.node_dict[vertex_name])

		for vertex_name in arg:
			node1 = self.node_dict[vertex_name]
			for adjacent_name in arg[vertex_name]:
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
	"""docstring for Player"""
	def __init__(self):
		super(Player, self).__init__()



class RandomPlayer(Player):
	"""docstring for RandomPlayer"""
	def __init__(self):
		super(RandomPlayer, self).__init__()

	def give_output(self, input):
		graph = Network(json.loads(input))

		





def main():
	graph = Network({"0": ["1", "3"], "1": ["0", "2"], "2": ["1", "3"], "3": ["0", "2"]})

	print graph.diameter()

	print graph.get_node("2").degree()

if __name__ == '__main__':
	main()
