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

# calculates Pearson correlation 
# denominator1 is the partial denominator for the first element
def pearsonCorrelation(el1, e2, denominator1=None):
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
            #el2 share some conditions with el1, check the therapies
            th2 = [x[0] for x in el2[condition]]
            for trial in el1[condition]:
                if(trial[1] != None):
                    if trial[0] in th2:
                        t2 = el2[condition][th2.index(trial[0])][1]
                        if(t2 != None):
                            # print("Something in common")
                            if condition in common:
                                common[condition].append(trial[0])
                            else:
                                common[condition] = [trial[0]]
                            #the same therapy list has been applied between the two
                            numerator += trial[1]*t2
        
        #get the denumerator part for el1
        if(denominator1 == None):
            for trial in el1[condition]:
                if (trial[1] != None):
                    partial += math.pow(trial[1], 2)
    if (partial == 0):
        partial = 1
    # print("Partial1 for el1: "+str(partial))
    if(denominator1 == None):
        denominator = denominator * math.sqrt(partial)
    elif denominator1 != 0:
        denominator = denominator * denominator1
    #get the denominator part for el2
    partial = 0
    for condition in el2:
        for trial in el2[condition]:
            if (trial[1] != None):
                partial += math.pow(trial[1], 2)
    if(partial == 0):
        partial = 1
    # print("Partial1 for el2: "+str(partial))
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
    print("PEARSON:"+str(pearsonCorrelation(patients[3], patients[i])))
    print("\n")


