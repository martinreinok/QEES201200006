# QEES201200006
Quantitative Evaluation of Embedded Systems course at University of Twente

# Project's goal 
Create model checker to find optimal battery-aware experiment schedules for the GOMX-3 nanosatellite. Part 3 of the project focuses on validating computed schedules using a kinetic battery model. Models are created for running with [Modest toolset](https://www.modestchecker.net/).


# Part 2
## Overview
We make no assumptions of satellite previous jobs.  
We have a large cost for skipping a job and even larger cost for empting the battery, so the model will always try to take a job.  

## Dynamic cost
To enforce "all jobs must be taken at least once" and 2:1 ration for X_BAND : L_BAND jobs, we use dynamic cost functions for each job, based on the "jobs_done" variables, that keep count how many jobs have been done. Dynamic cost function assigns a cost from 0 to 3, trying to balance the load between same band jobs, and keep the ratio. Here is an example:  
l_3f2_jobs_done = 1  
l_3f3_jobs_done = 2  
x_toulou_jobs_done = 1  
x_kourou_jobs_done = 3  
Cost for picking next job:  
3f2: 1, 3f3: 3, xt: 0, xk: 2  

## Schedule Modest
Modest result:  
550 minutes (750k states done in ~4 seconds)  
39 -> 67 	X Toulouse  
119 -> 145 	X Kourou  
168 -> 301 	3F2  
322 -> 455  3F3  
(All UHF jobs are taken)  
55 -> 59 	UHF  
147 -> 155 	UHF  
241 -> 251 	UHF  
336 -> 346 	UHF  
431 -> 440  UHF

## Schedule Python
550 minutes (750k states done in ~151 seconds)  
39 (2340) -> 67 (4020) 	X Toulouse  
119 (7140) -> 145 (8700)	X Kourou  
168 (10080) -> 301 (18060) 	3F2  
322 (19320) -> 455 (27300)  3F3  
(All UHF jobs are taken)  
55 -> 59 	UHF  
147 -> 155 	UHF  
241 -> 251 	UHF  
336 -> 346 	UHF  
431 -> 440  UHF

# Part 3
Initially our model was unable to produce proper schedule, we did some fixes to our model:
We reworked our LBAND sun extra power, which was not working properly before.
We modified the costs so the model would skip jobs more often.
Finally we adjusted the battery_empty to a higher value (from 0.4 to 0.5) which resulted in a working schedule.
The empty level adjustment results in a safer job selection, however all jobs are still complited at least once:

## Schedule Python
600 minutes (750k states done in ~151 seconds)  
39  (2340) -> 67  (4020)     X Toulouse
119 (7140) -> 145 (8700)     X Kourou
221(13260) -> 354 (21240)    3F3
366(21960) -> 499 (29940)    3F2
(All UHF jobs are taken)  
55  -> 59 	UHF
147 -> 155 	UHF
241 -> 251 	UHF
336 -> 346 	UHF  
431 -> 440  	UHF
528 -> 532	UHF
Full schedule in file: schedule_PYTHON.txt 


The "reformat_python_traces.py" generates a more readable traces from origial "checker.py" output.
This output can be seen in "schedule_PYTHON.txt"

These arrays are plugged to the modest simulation and the output are plotted, results can be seen in "KineticBatterySimulation.png"

## Kinetic battery model simulation result
![Results](./KineticBatterySimulation.png)

