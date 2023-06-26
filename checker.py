# Run as python checker-demo.py model.py
# Requires Python 3.7 or newer

import sys
import time
from timeit import default_timer as timer
from datetime import datetime
from multiprocessing import Process
import heapq
import os
from importlib import util
import shutil
from heapq import heappush, heappop
from collections import deque

# import the module
if len(sys.argv) < 2:
	print("Error: No model specified.")
	quit()
# Load the model
print("Loading model from \"{0}\"...".format(sys.argv[1]), end="", flush=True)
spec = util.spec_from_file_location("model", sys.argv[1])
model = util.module_from_spec(spec)
spec.loader.exec_module(model)
network = model.Network()  # create network instance


def get_properties_data(network):
	properties = {}
	for i in range(len(network.properties)):
		properties[i] = {}
		# Name
		properties[i].update({"name": f"{str(network.properties[i]).split(' ')[0]}"})

		# Reach
		is_reach = network.properties[i].exp is not None and network.properties[i].exp.op == "exists" and (
				network.properties[i].exp.args[0].op == "eventually" and
				network.properties[i].exp.args[0].args[0].op == "ap" or network.properties[i].exp.args[
					0].op == "until" and
				network.properties[i].exp.args[0].args[0].op == "ap" and network.properties[i].exp.args[0].args[
					0].op == "ap")
		properties[i].update({"reach": is_reach})

		# Safe and Goal Exp
		safe_exp = -1
		goal_exp = -1
		if is_reach:
			safe_exp = network.properties[i].exp.args[0].args[0].args[0] if \
				network.properties[i].exp.args[0].op == "until" else -1
			goal_exp = network.properties[i].exp.args[0].args[1].args[0] if \
				network.properties[i].exp.args[0].op == "until" else network.properties[i].exp.args[0].args[0].args[0]

		properties[i].update({"safe": safe_exp})
		properties[i].update({"goal": goal_exp})

		# Reward
		is_reward = network.properties[i].exp is not None and network.properties[i].exp.op == "e_min_s" and \
					network.properties[i].exp.args[1].op == "ap"
		if is_reward:
			properties[i].update({"reward": [network.properties[i].exp.args[0]]})
			properties[i].update({"goal": network.properties[i].exp.args[1].args[0]})
	return properties


def find_min_cost(_property, print_states=False, is_reach=False):
	state = network.get_initial_state()
	queue = [state]  # use a priority queue with cost as the first element
	costs = {state: 0}  # store costs in a dictionary
	predecessors = {state: None}  # store predecessor state and transition in a single dictionary
	safe_exp = _property.get("safe")
	while queue:
		if print_states:
			print(state)
		if is_reach:
			# This should be breath first check for reachability properties
			state = queue.pop()
		else:
			# find state with lowest cost in queue
			min_cost = float('inf')
			min_cost_state = None
			for state in queue:
				if costs[state] < min_cost:
					min_cost = costs[state]
					min_cost_state = state
			queue.remove(min_cost_state)
			state = min_cost_state

		is_goal = network.get_expression_value(state, _property.get("goal"))
		is_safe = True if safe_exp == -1 else network.get_expression_value(state, safe_exp)
		if is_goal:
			# reconstruct path by following predecessors back to the initial state
			path = []
			pre_state = predecessors[state]
			while pre_state is not None:
				path.append(str(state))
				label = get_transition_label(pre_state[0], state)
				if label != "tick":
					# tick transitions are not printed int the states.
					path.append(f"TRANSITION: {label}")
				state, transition = pre_state
				pre_state = predecessors[state]
			path.append(str(network.get_initial_state()))
			if is_reach:
				return write_results(_property.get("name"), True, path[::-1], True)
			return write_results(_property.get("name"), min_cost, path[::-1], True)

		for transition in network.get_transitions(state):
			if is_reach:
				if is_safe:
					new_state = network.jump_np(state, transition, [])
					if new_state not in predecessors:
						predecessors[new_state] = (state, transition)
						queue.append(new_state)
			else:
				jump_reward = _property.get("reward").copy()
				new_state = network.jump_np(state, transition, jump_reward)
				reward_in_state = min_cost + jump_reward[0]
				if reward_in_state < costs.get(new_state, float('inf')):  # update cost if it is lower
					costs[new_state] = reward_in_state
					predecessors[new_state] = (state, transition)
					queue.append(new_state)
	if is_reach:
		return write_results(_property.get("name"), False, None, False)
	return write_results(_property.get("name"), float('inf'), None, False)


class CostState(object):
	__slots__ = ("cost", "state")

	def __init__(self, cost: int, state):
		self.cost = cost
		self.state = state

	# def __eq__(self, other):
	# return self.cost == other.cost
	def __lt__(self, other):
		return self.cost < other.cost


def cost(_property, print_states=False):
	state = network.get_initial_state()
	queue = [CostState(0, state)]
	costs = {state: 0}  # store costs in a dictionary
	predecessors = {state: None}  # store predecessor state and transition in a single dictionary
	while queue:
		if print_states:
			print(queue[0].state)
		# find state with lowest cost in queue
		min_cost_state = heapq.heappop(queue)
		min_cost, state = min_cost_state.cost, min_cost_state.state

		is_goal = network.get_expression_value(state, _property.get("goal"))
		if is_goal:
			print("Goal reached")
			# reconstruct path by following predecessors back to the initial state
			path = []
			pre_state = predecessors[state]
			while pre_state is not None:
				path.append(str(state))
				label = get_transition_label(pre_state[0], state)
				if label != "tick":
					# tick transitions are not printed int the states.
					path.append(f"TRANSITION: {label}")
				state, transition = pre_state
				pre_state = predecessors[state]
			path.append(str(network.get_initial_state()))
			return write_results(_property.get("name"), min_cost, path[::-1], True)

		for transition in network.get_transitions(state):
			jump_reward = _property.get("reward").copy()
			new_state = network.jump_np(state, transition, jump_reward)
			reward_in_state = min_cost + jump_reward[0]
			if reward_in_state < costs.get(new_state, float('inf')):  # update cost if it is lower
				costs[new_state] = reward_in_state
				predecessors[new_state] = (state, transition)
				heapq.heappush(queue, CostState(reward_in_state, new_state))
	return write_results(_property.get("name"), float('inf'), None, False)


def get_transition_label(source_state, destination_state):
	if source_state == 0:
		source_state = network.get_initial_state()
	transitions = network.get_transitions(source_state)
	for transition in transitions:
		state = network.jump_np(source_state, transition, [])
		if state == destination_state:
			return network.transition_labels[transition.label]
	return None


def write_results(name, success, traces, print_traces):
	if not os.path.exists("./.results"):
		os.mkdir(".results")
	try:
		with open(f".results/{name.replace(':', '')}", "w", encoding="utf-8") as property_results:
			property_results.write(f"{name} {success}\n")
			if success and traces is not None and print_traces:
				for index, trace in enumerate(traces):
					property_results.write(f"*** {str(trace)}\n")
	except Exception as error:
		print(f"\n** {name} Unknown : {error}\n")


if __name__ == "__main__":
	DELETE_FILES = True
	PRINT_TRACES = True
	SAVE_RESULT_FILES = True
	start_time = timer()

	# Properties
	properties = get_properties_data(network)
	"""
	name; reach; safe; goal; reward;
	"""
	print("* The model has", str(len(network.properties)), "properties:")
	for i in properties:
		print(properties[i])

	threads = []
	THREADED = False
	print(f"Start time: {datetime.now().time()}")
	# NOTE: Threading doesn't help (GIL), multiprocessing does help
	# NOTE: Multiprocessing only improves performance if is more than one property
	for i in properties:

		# Check reach
		if properties[i].get("reach"):
			if THREADED:
				reach = Process(target=find_min_cost, daemon=False, args=(properties[i], False, True))
				reach.start()
				threads.append(reach)
			else:
				find_min_cost(properties[i], print_states=False, is_reach=True)

		# Check cost
		if properties[i].get("reward"):
			if THREADED:
				min_cost = Process(target=cost, daemon=False, args=(properties[i], True))
				min_cost.start()
				threads.append(min_cost)
			else:
				cost(properties[i], print_states=False)

	for i in threads:
		i.join()

	results = []
	if os.path.exists("./.results"):
		property_results = os.listdir("./.results")
		for _property in property_results:
			data = [x.strip() for x in open(f"./.results/{_property}", encoding="utf-8")]
			results.append([data[0].split(" "), [x for x in data[1:]]])
	else:
		for i in properties:
			print(f"\n** {properties[i].get('name')} Unknown")
			print(f"File write error has occurred\n")

	result_exists = [x[0][0] for x in results]
	for i in properties:
		if properties[i].get("name") not in result_exists:
			print(f"\n** {properties[i].get('name')} Unknown")

	for _property in results:
		print(f"\n** {_property[0][0]} {_property[0][1]}")
		if PRINT_TRACES:
			for trace in _property[1]:
				print(f"{trace}")

	if SAVE_RESULT_FILES:
		if os.path.exists("./results"):
			try:
				shutil.rmtree("./results")
			except:
				print("Error deleting directory")
		shutil.copytree("./.results", "./results")

	if os.path.exists("./.results"):
		try:
			shutil.rmtree("./.results")
		except:
			print("Error deleting directory")
	end_time = timer()
	# print(f"\nAnalyzed up to {len(max([x[2] for x in results]))} states")
	print("\nDone in {0:.2f} seconds.".format(end_time - start_time))
