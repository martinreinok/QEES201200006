"""
Converts python output file into a readable form with only "time", "battery_load", "battery_charge" and transitions
Also creates arrays for kinetic modest model.
"""

kinetic_times = []
kinetic_loads = []


def refactor_tuple(line):
	line = line.replace("*** ", "").replace("(", "").replace(")", "")
	line = line[line.index(" time"):]
	pairs = [i.split("=") for i in line.split(",")]
	line_dictionary = {i[0].replace(" ", ""): str(i[1].replace(" ", "")) for i in pairs}
	preserve = ["time", "battery_load", "battery_charge"]
	filtered_dict = {k: line_dictionary[k] for k in preserve if k in line_dictionary}
	kinetic_times.append(int(filtered_dict.get("time")))
	kinetic_loads.append(int(filtered_dict.get("battery_load")))
	return str(filtered_dict)


def extract_transition_lines(filepath, output):
	# Open the file for reading
	with open(filepath, 'r') as f:
		lines = f.readlines()
	with open(output, 'w') as f:
		for i, line in enumerate(lines):
			if '*** TRANSITION' in line:
				# f.writelines(refactor_tuple(lines[i - 1]))
				f.writelines("\n" + line)
				f.writelines(refactor_tuple(lines[i + 1]))
	# f.write('\n')


extract_transition_lines("results/EfficientRoute", "results/RefactoredOutput.txt")

print(f"const int LEN = {len(kinetic_times)};")
print(f"transient real[] times = {kinetic_times};")
print(f"transient real[] loads =  {kinetic_loads};\n")
