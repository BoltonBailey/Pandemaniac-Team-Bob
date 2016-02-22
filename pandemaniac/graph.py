import json
import random
import sim
import networkx as nx
import os



class Game(object):
	"""docstring for graph"""
	def __init__(self):
		super(Game, self).__init__()

		self.num_players = None
		self.num_seeds = None
		self.id = None

		self.network = None


	def get_degree(self, node):
		return len(self.adjacency_dict[node])




def game_from_file(filename):

	game = Game()
	game.network = nx.from_dict_of_lists(json.loads(open(filename).read()))


	# We split up the graphname, to get
	# -the number of players,
	# -the number of seed per player,
	# -the graph id.
	basename = os.path.basename(filename)

	num_list = map(int, basename.split(".")[:3])

	game.num_players = num_list[0]
	game.num_seeds = num_list[1]
	game.id = num_list[2]

	return game


def game_erdos_renyi(num_players, num_seeds, n, p):

	game = Game()

	game.network = nx.erdos_renyi_graph(n, p)
	game.network = nx.relabel_nodes(game.network, lambda x: str(x))

	game.num_players = num_players
	game.num_seeds = num_seeds

	game.id = "erdos_renyi_graph" + str(n) + "," + str(p)

	return game




class Player(object):
	"""The Player class is an abstract class for strategies for playing."""
	def __init__(self):
		super(Player, self).__init__()


	def give_50_output_to_file(self, game):
		""" This method causes the player to output its selections to an
		ouput file, for 50 rounds of the game."""


		file = open("output_files/" + str(game.num_players) + "." + str(game.num_seeds) + "." + str(game.id) + ".output" , "w+")

		for i in range(50):
			output = self.give_output_list(game)
			assert len(output) == game.num_seeds
			for node in self.give_output_list(game):
				file.write(node + "\n")

		file.close()



class RandomPlayer(Player):
	"""docstring for RandomPlayer"""
	def __init__(self):
		Player.__init__(self)


	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The random player
		chooses these randomly."""

		# Create a set of selections.
		selections = set()

		# Randomly add nodes until we have the right number of seeds
		while len(selections) < game.num_seeds:
			selections.add(random.choice(nx.nodes(game.network)))

		assert len(selections) == game.num_seeds
		return list(selections)


class HighDegreePlayer(Player):

	def __init__(self):
		Player.__init__(self)

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The high degree player
		chooses the largest degrees it can find."""

		nodes = nx.nodes(game.network)

		nodes.sort(key=lambda x : nx.degree(game.network, x), reverse=True)

		selections = nodes[:game.num_seeds]
		assert len(selections) == game.num_seeds
		return selections



class TwinAttackPlayer(Player):

	def __init__(self):
		Player.__init__(self)

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The twin attack player
		finds the highest degree nodes, and for each, it selects two
		neighbors of that node and"""

		nodes = nx.nodes(game.network)

		nodes.sort(key=lambda x : nx.degree(game.network, x), reverse=True)

		selections = set()

		for node in nodes:

			adjacents = list(nx.all_neighbors(game.network, node))

			for adj_node in adjacents[:2]:

				selections.add(adj_node)
				if len(selections) == game.num_seeds:
					break

			if len(selections) == game.num_seeds:
				break

		assert len(selections) == game.num_seeds
		return list(selections)

class ClosenessPlayer(Player):

	def __init__(self):
		Player.__init__(self)

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The twin attack player
		finds the highest degree nodes, and for each, it selects two
		neighbors of that node and"""

		nodes = nx.nodes(game.network)

		nodes.sort(key=lambda x : nx.closeness_centrality(game.network, x), reverse=True)

		selections = nodes[:game.num_seeds]

		assert len(selections) == game.num_seeds
		return list(selections)


class BetweenessPlayer(Player):

	def __init__(self):
		Player.__init__(self)

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The twin attack player
		finds the highest degree nodes, and for each, it selects two
		neighbors of that node and"""

		nodes = nx.nodes(game.network)

		between_dict = nx.betweenness_centrality(game.network, len(nodes)/10)

		nodes.sort(key=lambda x : between_dict[x], reverse=True)

		selections = nodes[:game.num_seeds]

		assert len(selections) == game.num_seeds
		return list(selections)


class FunctionPlayer(Player):
	"""docstring for FunctionPlayer"""
	def __init__(self, f):
		super(FunctionPlayer, self).__init__()
		# function that takes G and x
		self.function = f

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The twin attack player
		finds the highest degree nodes, and for each, it selects two
		neighbors of that node and"""

		nodes = nx.nodes(game.network)

		nodes.sort(key=lambda x : self.function(game.network, x), reverse=True)

		selections = nodes[:game.num_seeds]

		assert len(selections) == game.num_seeds
		return list(selections)



class DictFunctionPlayer(Player):
	"""docstring for DictFunctionPlayer"""
	def __init__(self, f):
		super(DictFunctionPlayer, self).__init__()
		# function that takes G and x
		self.function = f

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The twin attack player
		finds the highest degree nodes, and for each, it selects two
		neighbors of that node and"""

		nodes = nx.nodes(game.network)

		value_dict = self.function(game.network)

		nodes.sort(key=lambda x : value_dict[x], reverse=True)

		selections = nodes[:game.num_seeds]

		assert len(selections) == game.num_seeds
		return list(selections)


class SmartPlayer(Player):
	def __init__(self):
		super(SmartPlayer, self).__init__()

		self.game_memo_dict = {}

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The twin attack player
		finds the highest degree nodes, and for each, it selects two
		neighbors of that node and"""

		if game in self.game_memo_dict:
			return self.game_memo_dict[game]

		nodes = nx.nodes(game.network)

		value_dict = nx.degree_centrality(game.network)

		nodes.sort(key=lambda x : value_dict[x], reverse=True)

		candidate_nodes = nodes[:game.num_seeds * 2]

		candidate_nodes.sort(key=lambda x : nx.closeness_centrality(game.network, x), reverse=True)

		selections = candidate_nodes[:game.num_seeds]

		assert len(selections) == game.num_seeds
		self.game_memo_dict[game] = selections

		return list(selections)


class BeatDegreePlayer(Player):
	"""docstring for BeatDegreePlayer"""
	def __init__(self):
		super(BeatDegreePlayer, self).__init__()

		self.game_memo_dict = {}

	def give_output_list(self, game):
		""" This returns a list of the selected nodes. The twin attack player
		finds the highest degree nodes, and for each, it selects two
		neighbors of that node and"""

		# First, find out what the TA is doing.

		if game in self.game_memo_dict:
			return self.game_memo_dict[game]

		nodes = nx.nodes(game.network)

		value_dict = nx.degree_centrality(game.network)
		nodes.sort(key=lambda x : value_dict[x], reverse=True)

		ta_output_list = nodes[:game.num_seeds]



		candidate_nodes = nodes[:25]

		i = 0
		while i < 10000000:
			i += 1

			selections = set()
			while len(selections) < game.num_seeds:
				selections.add(random.choice(candidate_nodes))
			selections = list(selections)

			result = sim.run(nx.to_dict_of_lists(game.network), {"s0" : ta_output_list, "s1" : selections})

			if result["s0"] < result["s1"]:
				break


		assert len(selections) == game.num_seeds
		self.game_memo_dict[game] = selections

		return list(selections)



def play(game, playerlist):

	assert game.num_players == len(playerlist)

	graph = nx.to_dict_of_lists(game.network)

	nodes = {}

	for i, player in enumerate(playerlist):
		nodes["strategy" + str(i)] = player.give_output_list(game)
		assert len(nodes["strategy" + str(i)]) == game.num_seeds
		#print nodes["strategy" + str(i)]
	#print

	result = sim.run(graph, nodes)

	return result



def test_2p_5s_100n(playerlist):
	""" Plays a lot of games with the players in playerlist.
	Plays 2 player games with 5 seeds and 100 nodes, as we expect to occur.
	Should play with different graphs generated by networkx """

	wins = {player : 0 for player in playerlist}

	game_list = []

	for i in range(3, 13):
		for _ in range(10):
			# generate ~100 Erdos Renyi graphs, with p ranging from 0.3 to 0.10
			p = float(i)/100

			game = Game()
			game.num_players = 2
			game.num_seeds = 5
			game.id = 0

			game.network = nx.erdos_renyi_graph(100, p)

			game_list.append(game)

	for k in range(6, 14, 2): #4 possible
		for i in xrange(1, 25): # 25 possible
			# generate ~100 Watts-Strogatz graphs, with k ranging from 6 to 16
			# and p ranging from 0.10 to 0.50
			p = float(i)/50

			game = Game()
			game.num_players = 2
			game.num_seeds = 5
			game.id = 0

			game.network = nx.watts_strogatz_graph(100, k, p)

			game_list.append(game)


	for m in range(3, 13):
		for _ in range(10):
			# generate ~100 Barabasi-Albert graphs, with m ranging from 3 to 13
			game = Game()
			game.num_players = 2
			game.num_seeds = 5
			game.id = 0

			game.network = nx.barabasi_albert_graph(100, m)

			game_list.append(game)

	for game in game_list:
		for player1 in playerlist:
			for player2 in playerlist:
				result = play(game, [player1, player2])
				if result["strategy0"] > result["strategy1"]:
					wins[player1] += 1
				else:
				 	wins[player2] += 1


		for player in playerlist:
			print "score", wins[player]
		print


def report_on_given_graphs():

	game_list = []
	game_list.append(game_from_file("game_files/friday/2.5.1.json"))
	game_list.append(game_from_file("game_files/friday/2.10.10.json"))
	game_list.append(game_from_file("game_files/friday/2.10.20.json"))
	game_list.append(game_from_file("game_files/friday/2.10.30.json"))
	game_list.append(game_from_file("game_files/friday/4.5.1.json"))
	game_list.append(game_from_file("game_files/friday/4.10.1.json"))
	game_list.append(game_from_file("game_files/friday/8.10.1.json"))
	game_list.append(game_from_file("game_files/friday/8.20.1.json"))
	game_list.append(game_from_file("game_files/friday/8.20.2.json"))
	game_list.append(game_from_file("game_files/friday/8.35.1.json"))

	game_list.append(game_from_file("game_files/saturday/2.5.2.json"))
	game_list.append(game_from_file("game_files/saturday/2.10.11.json"))
	game_list.append(game_from_file("game_files/saturday/2.10.21.json"))
	game_list.append(game_from_file("game_files/saturday/2.10.31.json"))
	game_list.append(game_from_file("game_files/saturday/4.5.2.json"))
	game_list.append(game_from_file("game_files/saturday/4.10.2.json"))
	game_list.append(game_from_file("game_files/saturday/8.10.2.json"))
	game_list.append(game_from_file("game_files/saturday/8.20.3.json"))
	game_list.append(game_from_file("game_files/saturday/8.25.1.json"))
	game_list.append(game_from_file("game_files/saturday/8.35.2.json"))



	for game in game_list:
		print "Number of nodes:", len(nx.nodes(game.network))

	for game in game_list:
		print "Number of edges:", len(nx.edges(game.network))

	for game in game_list:
		print "Average degree:", float(2 * len(nx.edges(game.network)))/ len(nx.nodes(game.network))

	for game in game_list:
		print "Average connection probability:", float(2 * len(nx.edges(game.network)))/ len(nx.nodes(game.network))**2

	for game in game_list:
		print "Num connected components:", len(list(nx.connected_components(game.network)))

def main():
	# report_on_given_graphs()
	closeness_centrality_player = FunctionPlayer(nx.closeness_centrality)

	degree_centrality_player = DictFunctionPlayer(nx.degree_centrality)

	# Doesn't work on unconnected graphs
	# current_flow_closeness_centrality_player = DictFunctionPlayer(nx.current_flow_closeness_centrality)
	# eigenvector_centrality_player = DictFunctionPlayer(nx.eigenvector_centrality)
	#
	# def converted_katz_centrality(graph):
	# 	dict = {}
	# 	try:
	# 		dict = nx.katz_centrality(graph)
	# 	except:
	# 		dict = nx.degree_centrality(graph)
	# 	return dict
	#
	# katz_centrality_player = DictFunctionPlayer(converted_katz_centrality)
	# communicability_centrality_player = DictFunctionPlayer(nx.communicability_centrality)
	# load_centrality_player = DictFunctionPlayer(nx.load_centrality)
	#
	#

	# print play(
	# 	game_from_file("game_files/friday/8.35.1.json"),
	# 	[
	# 		degree_centrality_player,
	# 		SmartPlayer(),
	# 		degree_centrality_player,
	# 		RandomPlayer(),
	# 		RandomPlayer(),
	# 		RandomPlayer(),
	# 		RandomPlayer(),
	# 		RandomPlayer()
	# 	])

	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/2.5.2.json"))
	#
	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/4.5.2.json"))
	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/4.10.2.json"))
	#
	BeatDegreePlayer().give_50_output_to_file(game_from_file("game_files/sunday/2.10.12.json"))
	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/2.10.21.json"))
	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/2.10.31.json"))

	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/8.10.2.json"))
	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/8.20.3.json"))
	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/8.25.1.json"))
	# SmartPlayer().give_50_output_to_file(game_from_file("game_files/saturday/8.35.2.json"))

	# test_2p_5s_100n([degree_centrality_player, BeatDegreePlayer()])
	# print play(game_from_file("game_files/saturday/2.10.11.json"), [degree_centrality_player, BeatDegreePlayer()])
	# print play(game_from_file("game_files/friday/2.10.10.json"), [degree_centrality_player, BeatDegreePlayer()])

if __name__ == '__main__':
	main()
