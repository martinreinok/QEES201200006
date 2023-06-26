import datetime


class JobFile:
	name = str
	array = str


file1 = JobFile()
file1.name = "satellite_data/Sun.csv"
file1.array = "sun"
file2 = JobFile()
file2.name = "satellite_data/UHF.csv"
file2.array = "uhf"
file3 = JobFile()
file3.name = "satellite_data/L-Band-Inmarsat-3F2.csv"
file3.array = "l_band_3f2"
file4 = JobFile()
file4.name = "satellite_data/L-Band-Inmarsat-3F3.csv"
file4.array = "l_band_3f3"
file5 = JobFile()
file5.name = "satellite_data/X-Band-Kourou.csv"
file5.array = "x_band_kourou"
file6 = JobFile()
file6.name = "satellite_data/X-Band-Toulouse.csv"
file6.array = "x_band_toulouse"

filenames = [file1, file2, file3, file4, file5, file6]

START_DATE = "2016/03/20"
START_CLOCK = "21:00:00"
END_DATE = "2016/03/21"
END_CLOCK = "21:00:00"


def compare_datetime(date1, clock1, date2, clock2):
	"""Returns true if date1 >= date2"""
	date_1 = date1.split("/")
	date_2 = date2.split("/")
	clock_1 = clock1.split(":")
	clock_2 = clock2.split(":")
	# yyyy, mm, dd, hh, mm, ss
	d1 = datetime.datetime(int(date_1[0]), int(date_1[1]), int(date_1[2]), int(clock_1[0]), int(clock_1[1]),
						   int(clock_1[2]))
	d2 = datetime.datetime(int(date_2[0]), int(date_2[1]), int(date_2[2]), int(clock_2[0]), int(clock_2[1]),
						   int(clock_2[2]))

	return d1 > d2


def convert_date_to_seconds(date2, clock2):
	date_1 = START_DATE.split("/")
	date_2 = date2.split("/")
	clock_1 = START_CLOCK.split(":")
	clock_2 = clock2.split(":")
	# yyyy, mm, dd, hh, mm, ss
	start_seconds = datetime.datetime(int(date_1[0]), int(date_1[1]), int(date_1[2]),
									  int(clock_1[0]), int(clock_1[1]), int(clock_1[2])).timestamp()
	end_seconds = datetime.datetime(int(date_2[0]), int(date_2[1]), int(date_2[2]),
									int(clock_2[0]), int(clock_2[1]), int(clock_2[2])).timestamp()
	return int(end_seconds - start_seconds)


def select_function_name(file):
	if "3F2" in file:
		return "l_band_3f2"
	elif "3F3" in file:
		return "l_band_3f3"
	elif "Sun" in file:
		return "sun"
	elif "UHF" in file:
		return "uhf"
	elif "Kourou" in file:
		return "x_band_kourou"
	elif "Toulouse" in file:
		return "x_band_toulouse"


print("###############################################################################################################")
print("// ### Generated using generate_modest_time_structure.py")
print(f"const int MAX_TIME = 410;")
for file in filenames:
	in_range_data = []
	data = [x.strip().split(',') for x in open(file.name)][1:]
	for index, i in enumerate(data):
		# [['START_DATE', 'START_CLOCK'], ['END_DATE', 'END_CLOCK'], 'DURATION']
		data[index] = [i[0].split(" "), i[1].split(" "), i[2]]

	for event in data:
		start_time, end_time, duration = event
		start_date, start_clock = start_time
		end_date, end_clock = end_time
		duration = int(duration)

		if compare_datetime(start_date, start_clock, START_DATE, START_CLOCK) and compare_datetime(END_DATE, END_CLOCK,
																								   end_date, end_clock):
			seconds = convert_date_to_seconds(start_date, start_clock)
			in_range_data.append([seconds, seconds + duration])

	conversion = 60  # Seconds
	# """
	print(f"int(0..100000000)[] {file.array.upper()}_START = [", end="")
	for index, event in enumerate(in_range_data):
		if event == in_range_data[-1]:
			print(f"{event[0] // conversion}, 100000000];")
		else:
			print(f"{event[0] // conversion}, ", end="")

	print(f"int(0..100000000)[] {file.array.upper()}_END = [", end="")
	for index, event in enumerate(in_range_data):
		if event == in_range_data[-1]:
			print(f"{event[1] // conversion}, 100000000];")
		else:
			print(f"{event[1] // conversion}, ", end="")
	print(f"const int {file.array.upper()}_LEN = {len(in_range_data)};")
	print(f"int(0..{file.array.upper()}_LEN + 1) {file.array.lower()}_i = 0;")
	print("")
	# """
	"""
	print(f"function bool {file.array.upper()}(int time)")
	for index, event in enumerate(in_range_data):
		if index == 0:
			print(f"= if (time >= {event[0] // conversion} && time <= {event[1] // conversion}) then true")
		elif event == in_range_data[-1]:
			print(f"else if (time >= {event[0] // conversion} && time <= {event[1] // conversion}) then true else false;")
		else:
			print(f"else if (time >= {event[0] // conversion} && time <= {event[1] // conversion}) then true")
	print("")
	"""
print("// ###")
