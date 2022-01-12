import json
import copy
import math

#reads the json dataset and return a dictionary
def readJson(filename='datasets/datasetB.json'):
    f = open(filename)
    return json.load(f)

# Return a list of P (number of patients) length, each cell is a dictionary, 
# where the keys are the conditions for the patient and the values a list of couples (therapies, success), in form of list, 
# where therapies is the list of therapies applied (therapy id) and success is the success rate (0-100)
# Use a list of couples because the therapies applied are grouped, 
# for example (T1-30%, T2-40%, T3-100%) becomes (T1-30%; T1,T2-40%; T1,T2,T3-100%), this is done to consider temporal informations 
# and better compare the different data
def createDataset(dataset):
    #create the list and initialize with empty dicts
    ret = []
    for i in range(0, len(dataset["Patients"])):
        ret.append({})
    #for each patient fill the dictionary with conditions and therapies
    for i in range(0, len(dataset["Patients"])):
        #list of all trials done by that patient
        trials = dataset["Patients"][i]["trials"]

        for condition in dataset["Patients"][i]["conditions"]:
            therapies = []
            diagnosed = condition["diagnosed"]
            cured = condition["cured"]
            for t in trials:
                succ = None
                if (t["start"] > diagnosed and (cured == None or t["start"] < cured)):
                    if(t["condition"] == condition["id"]):
                        succ = t["successful"]
                    #the trial is done when the patient has that condition
                    therapies.append([t["therapy"], succ, t["start"]])

            # print(condition["id"])
            # print(therapies)
            
            #sort the therapies by their start date
            therapies.sort(key=lambda x: x[2])
            #store only yhe important values, I'm not interested on the date anymore, just the order
            th = []
            for j in range(0, len(therapies)):
                th.append([therapies[j][0], therapies[j][1]])
            # print(th)
            #create all the possible groups of therapies, for example (th1, th2, th3) becomes ([th1], [th1,th2], [th1,th2,th3]) to store causality
            therapies = []
            for j in range(0, len(th)):
                if(j==0):
                    therapies.append([[th[0][0]], th[0][1]])
                else:
                    previous = [x for x in therapies[j-1][0]]
                    previous.append(th[j][0])
                    therapies.append([previous, th[j][1]])
            # print(therapies)
            ret[i][condition["kind"]]=therapies
    return ret

#normalize a patient for similarity, the patient is a dictionary
def normalizePatient(patient):
    ret = copy.deepcopy(patient)
    tot = 0
    num = 0
    for condition in ret:
        for trial in ret[condition]:
            if(trial[1] != None):
                tot += trial[1]
                num += 1
    if(num!=0):
        tot = tot/num
    else:
        tot=0
    # print("Tot: "+str(tot)+", num: "+str(num))
    for condition in ret:
        for trial in ret[condition]:
            if(trial[1] != None):
               trial[1] -= tot
    return ret

#longest common subsequence between two lists
def lcs_length(a, b):
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, ca in enumerate(a, 1):
        for j, cb in enumerate(b, 1):
            table[i][j] = (
                table[i - 1][j - 1] + 1 if ca == cb else
                max(table[i][j - 1], table[i - 1][j]))
    return table[-1][-1]

#compare one sequence of trials (list trial) of one patient with all the sequences of trials for one specific condition of an other patient
#based on LCS to keep the order information, normalized over the length of the longest element between the two trials of the patients
#returns the success rate of the second patient for the most similar trial and the similarity value
#makes the comparison only if the last therapy is the same for both, otherwise the value for that comparison is 0, this is because of how the different trials lists are made
def compareTrials(trial1, condition2):
    #trial1 is supposed to be a list containing only therapies (es. [th1, th2, th3], es2. [th1])
    #condition2 is supposed to be a list of lists of therapies(list) and the last success rate
        #(es. [ [[th1], 80], [[th1, th2, th3],100] ]
    similarity=[0,0,0]
    last = trial1[-1]
    for elem in condition2:
        if (elem[0][-1] == last):
            #they have the same final therapy applied, so check the similarity (that will be non-zero)
            sim = lcs_length(trial1, elem[0])
            if(sim > similarity[0] and elem[1] != None):
                #if it is more similar then the others and the success rate is defined, store both the values
                similarity[0] = sim
                similarity[1] = elem[1]
                similarity[2] = len(elem[0])
    
    return (similarity[0]/max(similarity[2], len(trial1)), similarity[1])

# calculates Pearson correlation 
# denominator1 is the partial denominator for the first element
# returns a value in the interval [-1;+1]
def pearsonCorrelation(el1, e2):
    #it is assumed that el1 is already normalized (for performance)
    #normalize the second 
    el2 = normalizePatient(e2)
    numerator = 0
    denominator = 1
    partial = 0
    common = {}
    for condition in el1:
        if (condition in el2):
            # print("Condition in el2")
            # el2 share some conditions with el1, check the therapies
            # th2 = [x[0] for x in el2[condition]]
            for trial in el1[condition]:
                if(trial[1] != None):
                    print("FOR CONDITION: "+str(condition)+" AND TRIAL FOR EL1: "+str(trial))
                    print("COMPARE WITH "+str(el2[condition]))
                    sim = compareTrials(trial[0], el2[condition])
                    print(sim)
                    if sim[0] != 0:
                        if condition in common:
                            common[condition].append(trial[0])
                        else:
                            common[condition] = [trial[0]]
                        #the same therapy list has been applied between the two
                        #TODO: take in consideration the similarity rate
                        numerator += trial[1]*sim[1]*sim[0]
            #also the denominator is calculated considering ONLY common conditions
            #get the denumerator part for el1
            for trial in el1[condition]:
                if (trial[1] != None):
                    partial += math.pow(trial[1], 2)
    if (partial == 0):
        partial = 1
    denominator = denominator * math.sqrt(partial)

    #get the denominator part for el2
    partial = 0
    for condition in el2:
        if condition in el1:
            for trial in el2[condition]:
                if (trial[1] != None):
                    partial += math.pow(trial[1], 2)
    if(partial == 0):
        partial = 1
    denominator = denominator * math.sqrt(partial)
    return numerator/denominator
    

#Read json dataset
dataset = readJson()
#Create patients list
patients = createDataset(dataset)
# print(patients[3])
a = normalizePatient(patients[3])
# print(a)


for i in range(0, len(patients)):
    print("PATIENT "+str(i))
    print("PEARSON:"+str(pearsonCorrelation(a, patients[i])))
    print("\n")

#TODO: order Patients based on similarity
#TODO: for each patient return the therapy that can be done and the success rate
#TODO: decide what to keep based on user similarity and success rate
