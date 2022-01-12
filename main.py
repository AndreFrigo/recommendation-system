import json
import copy

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
            ret[i][condition["id"]]=therapies
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
    
    tot = tot/num
    # print("Tot: "+str(tot)+", num: "+str(num))
    for condition in ret:
        for trial in ret[condition]:
            if(trial[1] != None):
               trial[1] -= tot
    return ret

# calculates Pearson correlation 
def pearsonCorrelation(el1, el2):
    #it is assumed that el1 and el2 are already normalized (for performance)


    pass

#Read json dataset
dataset = readJson()
#Create patients list
patients = createDataset(dataset)
print(patients[3])
a = normalizePatient(patients[3])
print(a)

# for i in range(0, len(patients)):
#     print("PATIENT "+str(i))
#     print(patients[i])
#     print("\n")


