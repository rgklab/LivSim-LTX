#!/sscc/opt/anaconda3/bin/python
import heapq
import numpy as nump
import scipy as scip
import datetime
import operator
import sys
import os
import queue
import csv
import ast
import pandas as pd
from copy import deepcopy
# from config import INPUT_DIRECTORY
import engine
import entity
import allocate
import event
import cProfile, pstats, io

maxtime = float(sys.argv[1])
nreps = int(sys.argv[2])
score = sys.argv[3]

# policy = ast.literal_eval(sys.argv[3])
# ShareU = ast.literal_eval(sys.argv[4])
# ShareL = ast.literal_eval(sys.argv[5])
# localboost = int(sys.argv[6])
# directory = sys.argv[7]

policy = [0, 0, 0, 0]
ShareU = 999999
ShareL = -999999
localboost = 0
directory = f'../LivSim_Output/{score}/'
INPUT_DIRECTORY = f'LivSim_Input/postprocessed/{score}'

if not os.path.exists(directory):
    os.makedirs(directory)


if __name__ =="__main__":
	#Check the inputs
	# if maxtime < 0 or maxtime > 5:
	# 	print("Invalid maxtime input.")
	# 	quit()
	#
	print(f'input directory {INPUT_DIRECTORY}')
	if nreps < 0 or nreps > 5:
		print("Invalid number of repetitions input.")
		quit()

	if len(policy) != 4:
		print("Invalid policy input.")
		quit()

	if all(isinstance(item, int) for item in policy) is False:
		print("Invalid policy input.")
		quit()

	if os.path.exists(directory) is False:
		print(directory)
		print("Invalid directory.")
		quit()
	if directory[-1] != "/":
		print("Does not have slash at the end. Please add.")
		quit()


	Sim = engine.G()
	nump.random.seed(Sim.seed)
	#   Input Data
	# exec(open('InputData_LivPlayback_1_11.py').read())

	import numpy as nump

	import entity

	#########################################################Setting########################################################
	# ndsa = 709  # number of DSAs 709 for SRTR
	ndsa = 867
	fake_ndsa = 58
	i_initial = 1  # Use initial waiting list 1=yes 0=no
	exclude_hi_pr = 0  # 1=Exclude Hawaii and Puerto Rico
	########################################################################################################################

	###################################################Uploading Input Files################################################
	print("Loading file")
	# DSA Geographic Relation Data
	# Regions = nump.loadtxt("C:/uoft-academic/livsim_research/LivSim-Codes-master/FakeInput/Input_Geography.txt")
	Regions = nump.loadtxt(f'../{INPUT_DIRECTORY}/SRTR_Input_Geography.txt')
	Regions = nump.reshape(Regions, (ndsa, ndsa))
	Regions = Regions.astype(int)
	print("Input_Geography.txt loaded.")

	# DSA Sharing Partner Data
	# SharingPartners = nump.loadtxt("C:/uoft-academic/livsim_research/LivSim-Codes-master/FakeInput/Input_SPartners2.txt")
	SharingPartners = nump.loadtxt(f"../{INPUT_DIRECTORY}/SRTR_Input_SPartners.txt")

	SharingPartners = nump.reshape(SharingPartners, (ndsa, ndsa))
	SharingPartners = SharingPartners.astype(int)
	print("Input_SPartners.txt loaded.")

	# Patient Arrival Input Data
	# PatientPlayback = nump.loadtxt("C:/uoft-academic/livsim_research/LivSim-Codes-master/FakeInput/fake_Patients.txt")
	PatientPlayback = pd.read_csv(f"../{INPUT_DIRECTORY}/SRTR_Patient.csv").to_numpy()

	print("Patients.txt loaded.")

	# Organ Input Data
	# OrganPlayback = nump.loadtxt("C:/uoft-academic/livsim_research/LivSim-Codes-master/FakeInput/fake_Donors.txt")
	OrganPlayback = pd.read_csv(f"../{INPUT_DIRECTORY}/SRTR_Donors.csv").to_numpy()
	print("Donors.txt loaded.")

	# Progession Input Data
	# ProgressionPlayback = nump.loadtxt("C:/uoft-academic/livsim_research/LivSim-Codes-master/FakeInput/fake_Status.txt")
	ProgressionPlayback = pd.read_csv(f"../{INPUT_DIRECTORY}/SRTR_Status.csv").to_numpy()
	print("Status.txt loaded.")

	# Relist Data
	Relist = nump.loadtxt("../FakeInput/Input_Relist.txt")
	print("Input_Relist.txt loaded.")

	# Acceptance Model Data
	AcceptanceModel = nump.loadtxt("../FakeInput/Input_Acceptance.txt")
	print("Input_Acceptance.txt loaded.")

	AcceptanceModelS1 = nump.loadtxt(
		"../FakeInput/Input_Acceptance_Status1.txt")
	print("Input_Acceptance_Status1.txt loaded.")

	DSA_Avg_Times = nump.loadtxt("../FakeInput/DSA_AvgTimes.txt")
	DSA_Avg_Times = nump.reshape(DSA_Avg_Times, (fake_ndsa, fake_ndsa))
	DSA_Avg_Times = DSA_Avg_Times.astype(float)
	print("DSA_AvgTimes.txt loaded.")

	# Donor Accept data which has contains organs that become available from the model start date through and including the model end date
	with open("../FakeInput/fake_Donor_Accept.txt", 'r') as inputf:
		reader = list(csv.reader(inputf, delimiter='|'))
		Donor_Accept = []
		for row in reader:
			Donor_Accept.append(row)
	print("Donor_Accept.txt loaded.")

	# Patient Accept data which contains all candidates on the waiting list as of the day befor the model start and new patinets
	# added to the waiting list with listing dats from the model start date through and including the model end date
	with open("../FakeInput/fake_Patients_Accept.txt", 'r') as inputf:
		reader = list(csv.reader(inputf, delimiter='|'))
		Patients_Accept = []
		for row in reader:
			Patients_Accept.append(row)
	print("Patients_Accept.txt loaded.")
	pr = cProfile.Profile()
	pr.enable()
	# Initial Waiting List
	OPTN_initial = [[] for i in range(0, ndsa)]
	initial_counts = 0 * nump.ndarray(shape=(ndsa, 1), dtype=int)
	if i_initial == 1:
		# upload initial waitlist of patients waiting for transplant
		InitialList = pd.read_csv(
			f"../{INPUT_DIRECTORY}/SRTR_Waitlist_matchmeld.csv")
		InitialList = InitialList.to_numpy()
		initialrows = nump.shape(InitialList)[0]

		# Based on inclusion of Hawaii and Puerto Rico, select appropriate column for DSA ids

		dsa_id_column = 1

		# init_prog_scheduler = []

		# iterate through list of patients of intial waitlist
		for i in range(0, initialrows):
			newpatient = entity.Patient(InitialList[i, 0].astype(int), InitialList[i, dsa_id_column].astype(int),
										InitialList[i, 2])  # construct patient object

			# record patient information in patient object
			newpatient.ABO = InitialList[i, 3].astype(int)
			newpatient.Status1 = InitialList[i, 6].astype(int)
			newpatient.Inactive = InitialList[i, 9].astype(int)
			if InitialList[i, 7] != ".":
				newpatient.Na = InitialList[i, 7].astype(int)
			else:
				newpatient.Na = 137
			labmeld = InitialList[i, 4].astype(int)

			# Assign MELD to Status1 HCC candidates
			if newpatient.Status1 == 1:
				newpatient.lMELD = 41
				newpatient.MELD = 41

			# Assign MELD and HCC for non-Status 1 candidates
			if newpatient.Status1 == 0:
				newpatient.HCC = InitialList[i, 5].astype(int)

			# if MELD sodium option is selected, compute MELD for non-HCC, non-Status1 patient based on sodium score
			if Sim.sodium == 1 and newpatient.Status1 == 0 and newpatient.HCC == 0:
				effective_na = newpatient.Na

				# set bound on sodium level
				if effective_na < 125:
					effective_na = 125
				elif effective_na > 137:
					effective_na = 137

				# set lab meld score
				newpatient.lMELD = labmeld

				# compute the allocation meld score
				newpatient.MELD = nump.rint(
					labmeld + 1.32 * (137 - effective_na) - (0.033 * labmeld * (137 - effective_na)))

			# if MELD sodium is option is not selected for non-HCC, non-Status1 patient, set patient's MELD to lab meld score
			elif Sim.sodium == 0 and newpatient.Status1 == 0 and newpatient.HCC == 0:
				newpatient.lMELD = labmeld
				newpatient.MELD = labmeld

			# if patient is HCC, adjust MELD score
			elif newpatient.HCC == 1:
				# If cap and delay not selected, adjust MELD score as follows.
				if Sim.capanddelay == 0:
					if labmeld <= 22:
						newpatient.MELD = 22
					elif labmeld <= 25 and labmeld > 22:
						newpatient.MELD = 25
					elif labmeld <= 28 and labmeld > 25:
						newpatient.MELD = 28
					elif labmeld <= 29 and labmeld > 28:
						newpatient.MELD = 29
					elif labmeld <= 31 and labmeld > 29:
						newpatient.MELD = 31
					elif labmeld <= 33 and labmeld > 31:
						newpatient.MELD = 33
					elif labmeld <= 34 and labmeld > 33:
						newpatient.MELD = 34
					elif labmeld <= 35 and labmeld > 34:
						newpatient.MELD = 35
					elif labmeld <= 37 and labmeld > 35:
						newpatient.MELD = 37
					elif labmeld > 37:
						newpatient.MELD = min(labmeld, 40)
				# if cap and delay is selected, adjust MELD score based on how long the patient waited by the start of the
				# model
				else:
					if (0 - newpatient.create_time) <= .5:
						newpatient.MELD = 28
					elif (0 - newpatient.create_time) > .5 and (0 - newpatient.create_time <= .75):
						newpatient.MELD = 29
					elif (0 - newpatient.create_time) > .75 and (0 - newpatient.create_time <= 1):
						newpatient.MELD = 31
					elif (0 - newpatient.create_time) > 1 and (0 - newpatient.create_time <= 1.25):
						newpatient.MELD = 33
					elif (0 - newpatient.create_time) > 1.25 and (0 - newpatient.create_time <= 1.5):
						newpatient.MELD = 34
					else:
						newpatient.MELD = min(labmeld, 40)
				# set lab meld score to allocation meld score
				newpatient.lMELD = newpatient.MELD

			# if newpatient.HCC ==1 and Sim.capanddelay ==0:
			#   init_prog_scheduler.append([.25, newpatient.DSA,newpatient.id])
			# elif newpatient.HCC ==1 and Sim.capanddelay ==1 and -newpatient.create_time <=.25:
			#   init_prog_scheduler.append([.5, newpatient.DSA,newpatient.id])
			# elif newpatient.HCC ==1 and Sim.capanddelay ==1 and -newpatient.create_time >.25:
			#   init_prog_scheduler.append([.25, newpatient.DSA,newpatient.id])
			# else:
			#   init_prog_scheduler.append([Sim.progtime, newpatient.DSA,newpatient.id])

			# record the number of patients in waiting list for each DSA
			initial_counts[newpatient.DSA] = initial_counts[newpatient.DSA] + 1

			# add the patient to the corresponding DSA waiting list
			if newpatient.DSA >= 0:
				OPTN_initial[newpatient.DSA].append(newpatient)
	print("Waitlist_matchmeld.txt loaded.")

	print("Simulation Input Complete. Starting simulation @ ", datetime.datetime.now().time())

	for reps in range(1,nreps+1):
	    #Initialize Replication
	    Sim.clock=0
	    #Sim.pid = 100000
	    Sim.oid = 0	

	    #Update parameters
	    Sim.maxtime = maxtime
	    Sim.nreps = nreps
	    Sim.regional_sharing = policy[0]
	    Sim.sodium = policy[1]
	    Sim.capanddelay = policy[2]
	    Sim.spartners = policy[3]
	    Sim.ShareU = ShareU
	    Sim.ShareL = ShareL
	    Sim.localboost = localboost

	    #Initialize Statistics
	    Stat = engine.SimStat()
	    Stat.yarrivals =    nump.zeros(shape=(ndsa,1),dtype=int)
	    Stat.ydeaths =      nump.zeros(shape=(ndsa,1),dtype=int)
	    Stat.yremoved =     nump.zeros(shape=(ndsa,1),dtype=int)
	    Stat.ytransplants = nump.zeros(shape=(ndsa,1),dtype=int)
	    Stat.ywait = nump.zeros(shape=(ndsa,1),dtype=float)
	    Stat.yMELD = nump.zeros(shape=(ndsa,1),dtype=int)
	    Stat.numcandidates =  deepcopy(initial_counts)
	    Stat.ycandidates =    deepcopy(Stat.numcandidates)
	    Stat.ymedMELD = [[] for i in range(0,ndsa)]
	    Stat.yrelists =     nump.zeros(shape=(ndsa,1),dtype=int)
	    Stat.yregrafts =    nump.zeros(shape=(ndsa,1),dtype=int)
	    print("Starting replication,  time is: ", datetime.datetime.now().time())	

	    #Initialize Waiting Lists
	    OPTN = deepcopy(OPTN_initial)	
	

	    #Schedule events for playback
	    scheduling_done =0
	    nextyear =1
	    Calendar = []	

	    #extract subset relted to the replications
	    subset_PatientPlayback = PatientPlayback[PatientPlayback[:,0] == reps]
	    subset_OrganPlayback = OrganPlayback[OrganPlayback[:,0] == reps]
	    subset_ProgressionPlayback = ProgressionPlayback[ProgressionPlayback[:,0] == reps]	

	    #set up index pointers
	    patient_index_pointer = 0
	    organ_index_pointer = 0
	    prog_index_pointer = 0	

	    #create indices
	    patient_index = nump.size(subset_PatientPlayback,0)-1
	    organ_index = nump.size(subset_OrganPlayback,0)-1
	    prog_index = nump.size(subset_ProgressionPlayback,0)-1	
	

	    while scheduling_done ==0:	

	        #next patient arrival
	        if patient_index_pointer <= patient_index:
	            nextarrival = subset_PatientPlayback[patient_index_pointer][4] #next arrival is next patient's arrival time
	        else:
	            nextarrival = Sim.maxtime +1 #next arrival is 1+Sim.maxtime	

	        #next organ arrival
	        if organ_index_pointer <= organ_index:
	            nextorgan = subset_OrganPlayback[organ_index_pointer][3] #next organ arrival is next organ's arrival time
	        else:
	            nextorgan = Sim.maxtime +1 #next organ arrival is 1+Sim.maxtime	

	        #next progression arrival
	        if prog_index_pointer <= prog_index:	

	            nextprog = subset_ProgressionPlayback[prog_index_pointer][2] #next progression is next status event time
	        else:
	            nextprog = Sim.maxtime +1 #next progression is 1+Sim.maxtime	
	
	

	        if nextyear == min(nextyear,nextarrival,nextorgan,nextprog,Sim.maxtime):
	        #if the next event is the next year, then record event as a Year and add to calendar
	            nextevent = engine.Event('Year',nextyear,[])
	            Calendar.append(nextevent)
	            nextyear = nextyear + 1	

	        elif nextarrival == min(nextarrival,nextorgan,nextprog,Sim.maxtime):
	        #if the next event is a patient arrival, record event as a patient arrival and add to calendar; update patient arrival pointer
	            nextevent = engine.Event('Arrival',nextarrival,subset_PatientPlayback[patient_index_pointer])
	            Calendar.append(nextevent)
	            patient_index_pointer = patient_index_pointer + 1	

	        elif nextorgan == min(nextorgan,nextprog,Sim.maxtime):
	        #if the next event is organ arrival, record event as organ arrival and add to calendar; update organ arrival pointer
	            nextevent = engine.Event('Organ',nextorgan,subset_OrganPlayback[organ_index_pointer])
	            Calendar.append(nextevent)
	            organ_index_pointer = organ_index_pointer + 1	

	        elif nextprog <= Sim.maxtime:
	        #if next event is progression, record event as progression and add to calendar. update pointer to next progression
	            nextevent = engine.Event('Progression',nextprog,subset_ProgressionPlayback[prog_index_pointer])
	            Calendar.append(nextevent)
	            prog_index_pointer = prog_index_pointer + 1
	        else:
	        #otherwise scheduling is done
	            scheduling_done =1	
	

	    # Simulation
	    while Calendar != []:
	        #obtains the next event of the calendar while also removing it from the calendar
	        nextevent = Calendar.pop(0)	

	        #if next event is year, call Year function to update simulation statistics
	        if nextevent.type == 'Year':
	            Sim.clock = nextevent.time
	            print("A year has passed.")
	            Sim, Stat = event.Year(Sim, Stat, reps)	

	        #if next event is patient arrival, call arrival function to add patient to the waitlist of the DSA
	        elif nextevent.type == 'Arrival':
	            Sim.clock = nextevent.time
	            Sim, Stat, OPTN = event.Arrival(nextevent.info, Sim, Stat, OPTN)	

	        #if next event is progression, call progression function to update patient's status
	        elif nextevent.type == 'Progression':
	            Sim.clock = nextevent.time
	            Sim, Stat, OPTN = event.Progression(nextevent.info, Sim, Stat, OPTN, reps)

	        #if next event is an organ arrival, call organ arrival function to allocate organ
	        elif nextevent.type == 'Organ':
	            Sim.clock = nextevent.time
	            Sim, Stat, OPTN = event.OrganArrival(nextevent.info, Sim, Stat, OPTN, Regions, SharingPartners, Patients_Accept, Donor_Accept, DSA_Avg_Times, AcceptanceModelS1, AcceptanceModel, Relist, reps)	
	

	    event.EndRep()	

	    del Stat	
	
	# get profiler result
	with open('output_cumulative.txt', 'w') as s:
		sortby = 'cumulative'
		ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
		ps.print_stats()


	#Output Results
	#convert arrays to data frames
	record_deaths = pd.DataFrame(data = Sim.record_deaths)
	record_deaths.columns = ['# of Deaths', 'Year', 'Replication #']	

	record_mr_disparity_mean = pd.DataFrame(data = Sim.record_mr_disparity_mean)
	record_mr_disparity_mean.columns = ['DSA Average Mortality Rate', 'Year', 'Replication #']	

	record_mr_disparity_std = pd.DataFrame(data = Sim.record_mr_disparity_std)
	record_mr_disparity_std.columns = ['DSA Mortality Rate Standard Deviation', 'Year', 'Replication #']	

	record_meld_disparity_mean = pd.DataFrame(data = Sim.record_meld_disparity_mean)
	record_meld_disparity_mean.columns = ['DSA Transplant Average MELD', 'Year', 'Replication #']	

	record_meld_disparity_std = pd.DataFrame(data = Sim.record_meld_disparity_std)
	record_meld_disparity_std.columns = ['Standard Deviation of Average DSA Transplant MELD', 'Year', 'Replication #']	

	record_medMELDmean = pd.DataFrame(data = Sim.record_medMELDmean)
	record_medMELDmean.columns = ['DSA Transplant MELD Median', 'Year', 'Replication #']	

	record_medMELDstd = pd.DataFrame(data = Sim.record_medMELDstd)
	record_medMELDstd.columns = ['Standard Deviation of DSA Transplant MELD Median', 'Year', 'Replication #']	

	DSA_column = ['Year', 'Replication #', 'Replication #']	

	# for i in range(0, 709): DSA_column.append("DSA {0}".format(i)) # DSA need to change
	for i in range(0, 867): DSA_column.append("DSA {0}".format(i))

	record_ydeaths = pd.DataFrame(data = Sim.record_ydeaths)
	record_ydeaths.columns = DSA_column	

	record_ytransplants = pd.DataFrame(data = Sim.record_ytransplants)
	record_ytransplants.columns = DSA_column	

	record_yarrivals = pd.DataFrame(data = Sim.record_yarrivals)
	record_yarrivals.columns = DSA_column	

	record_ycandidates = pd.DataFrame(data = Sim.record_ycandidates)
	record_ycandidates.columns = DSA_column	

	record_yremoved = pd.DataFrame(data = Sim.record_yremoved)
	record_yremoved.columns = DSA_column	

	record_ywait = pd.DataFrame(data = Sim.record_ywait)
	record_ywait.columns = DSA_column	

	record_yMELD = pd.DataFrame(data = Sim.record_yMELD)
	record_yMELD.columns = DSA_column	

	record_txDSA = pd.DataFrame(data = Sim.record_txDSA)
	record_txDSAoutput = pd.DataFrame(data = Sim.record_txDSAoutput)	

	record_removals = pd.DataFrame(data = Sim.record_removals)
	record_removals.columns = ['Year', 'Replication #', 'Removal Time', 'Removed Patient ID', 'Patient Allocation MELD', 'Patient Lab MELD']	

	#death record
	record_deathsID = pd.DataFrame(data=Sim.record_deathsID)
	record_deathsID.columns = ['Year', 'Replication #', 'Death Time', 'Death Patient ID', 'Patient Allocation MELD', 'Patient Lab MELD']

	record_txID = pd.DataFrame(data = Sim.record_txID)
	record_txID.columns = ['Year', 'Replication #', 'Transplant Time', 'Transplant Patient ID', 'Regional Transplant', 'National Transplant', 'Allocation MELD', 'Inactive']

	record_doID = pd.DataFrame(data = Sim.record_doID)
	record_doID.columns = ['Year', 'Replication #', 'Transplant Time', 'Transplant Patient ID', 'Donor ID']	

	yrelists = pd.DataFrame(data = Sim.record_yrelists)
	yrelists.columns = DSA_column	

	yregrafts = pd.DataFrame(data = Sim.record_yregrafts)
	yregrafts.columns = DSA_column	

	record_txIDregraft = pd.DataFrame(data = Sim.record_txIDregraft)
	record_txIDregraft.columns = ['Year', 'Replication #', 'Re-Transplant Time', 'Re-Transplant Patient ID', 'Regional Re-Transplant', 'National Re-Transplant']	

	record_doIDregraft = pd.DataFrame(data = Sim.record_doIDregraft)
	record_doIDregraft.columns = ['Year', 'Replication #', 'Re-Transplant Time', 'Re-Transplant Patient ID', 'Donor ID']	

	record_relists = pd.DataFrame(data = Sim.record_relists)
	record_relists.columns = ['Year', 'Replication #', '1st Transplant Time', 'Patient ID', 'Patient Allocation MELD at First Transplant Time', 'Patient Earliest Re-Transplant Time']	

	#Output Results
	nump.savetxt(directory + "Output_deaths.txt", Sim.record_deaths, fmt='%1.4e', delimiter='\t', newline='\n')
	record_deaths.to_csv(directory + "Output_deaths.csv", sep=',', encoding='utf-8', index = False)

	nump.savetxt(directory + "Output_mr_disparity_mean.txt", Sim.record_mr_disparity_mean, fmt='%1.4e', delimiter='\t', newline='\n')
	record_mr_disparity_mean.to_csv(directory + "Output_mr_disparity_mean.csv", sep=',', encoding='utf-8', index = False)

	nump.savetxt(directory + "Output_mr_disparity_std.txt", Sim.record_mr_disparity_std, fmt='%1.4e', delimiter='\t', newline='\n')
	record_mr_disparity_std.to_csv(directory + "Output_mr_disparity_std.csv", sep=',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "Output_meld_disparity_mean.txt", Sim.record_meld_disparity_mean, fmt='%1.4e', delimiter='\t', newline='\n')
	record_meld_disparity_mean.to_csv(directory + "Output_meld_disparity_mean.csv", sep=',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "Output_meld_disparity_std.txt", Sim.record_meld_disparity_std, fmt='%1.4e', delimiter='\t', newline='\n')
	record_meld_disparity_std.to_csv(directory + "Output_meld_disparity_std.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "Output_meld_median_mean.txt", Sim.record_medMELDmean, fmt='%1.4e', delimiter='\t', newline='\n')
	record_medMELDmean.to_csv(directory + "Output_meld_median_mean.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "Output_meld_median_std.txt", Sim.record_medMELDstd, fmt='%1.4e', delimiter='\t', newline='\n')
	record_medMELDstd.to_csv(directory + "Output_meld_median_std.csv", sep =',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_ydeaths.txt", Sim.record_ydeaths, fmt='%1.4e', delimiter='\t', newline='\n')
	record_ydeaths.to_csv(directory + "RawOutput_ydeaths.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_ytransplants.txt", Sim.record_ytransplants, fmt='%1.4e', delimiter='\t', newline='\n')
	record_ytransplants.to_csv(directory + "RawOutput_ytransplants.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_yarrivals.txt", Sim.record_yarrivals, fmt='%1.4e', delimiter='\t', newline='\n')
	record_yarrivals.to_csv(directory + "RawOutput_yarrivals.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_ycandidates.txt", Sim.record_ycandidates, fmt='%1.4e', delimiter='\t', newline='\n')
	record_ycandidates.to_csv(directory + "RawOutput_ycandidates.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_yremoved.txt", Sim.record_yremoved, fmt='%1.4e', delimiter='\t', newline='\n')
	record_yremoved.to_csv(directory + "RawOutput_yremoved.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_ywait.txt", Sim.record_ywait, fmt='%1.4e', delimiter='\t', newline='\n')
	record_ywait.to_csv(directory + "RawOutput_ywait.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_yMELD.txt", Sim.record_yMELD, fmt='%1.4e', delimiter='\t', newline='\n')
	record_yMELD.to_csv(directory + "RawOutput_yMELD.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_DSAs.txt", Sim.record_txDSA, fmt='%1.4e', delimiter='\t', newline='\n')
	record_txDSA.to_csv(directory + "RawOutput_DSAs.csv", sep = ',', encoding = 'utf-8')

	nump.savetxt(directory + "RawOutput_DSAs2.txt", Sim.record_txDSAoutput, fmt='%1.4e', delimiter='\t', newline='\n')
	record_txDSAoutput.to_csv(directory + "RawOutput_DSAs2.csv", sep = ',', encoding = 'utf-8')

	nump.savetxt(directory + "RawOutput_removals.txt", Sim.record_removals, fmt='%1.4e', delimiter='\t', newline='\n')
	record_removals.to_csv(directory + "RawOutput_removals.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_IDdeaths.txt", Sim.record_deathsID, fmt='%1.4e', delimiter='\t', newline='\n')
	record_deathsID.to_csv(directory + "RawOutput_IDdeaths.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_TxID.txt", Sim.record_txID, fmt='%1.4e', delimiter='\t', newline='\n')
	record_txID.to_csv(directory + "RawOutput_TxID.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_DoID.txt", Sim.record_doID, fmt='%1.4e', delimiter='\t', newline='\n')
	record_doID.to_csv(directory + "RawOutput_DoID.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_yrelists.txt", Sim.record_yrelists, fmt='%1.4e', delimiter='\t', newline='\n')
	yrelists.to_csv(directory + "RawOutput_yrelists.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_yregrafts.txt", Sim.record_yregrafts, fmt='%1.4e', delimiter='\t', newline='\n')
	yregrafts.to_csv(directory + "RawOutput_yregrafts.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_TxIDregraft.txt", Sim.record_txIDregraft, fmt='%1.4e', delimiter='\t', newline='\n')
	record_txIDregraft.to_csv(directory + "RawOutput_TxIDregraft.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_DoIDregraft.txt", Sim.record_doIDregraft, fmt='%1.4e', delimiter='\t', newline='\n')
	record_doIDregraft.to_csv(directory + "RawOutput_DoIDregraft.csv", sep = ',', encoding = 'utf-8', index = False)

	nump.savetxt(directory + "RawOutput_Relistid.txt", Sim.record_relists, fmt='%1.4e', delimiter='\t', newline='\n')
	record_relists.to_csv(directory + "RawOutput_Relistid.csv", sep = ',', encoding = 'utf-8', index = False)

	print('Simulation Finished @ ',datetime.datetime.now().time())