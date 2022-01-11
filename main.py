import json

#reads the json dataset and return a dictionary
def readJson(filename='datasets/datasetB.json'):
    f = open(filename)
    return json.load(f)

# Return a list of P (number of patients) length, each cell is a dictionary, 
# where the keys are the conditions for the patient and the values a list of couples (therapies, success),
# where therapies is the list of therapies applied (therapy id) and success is the success rate (0-100)
# Use a list of touples because the therapies applied are grouped, 
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
            # print("Condition: "+str(condition["id"])+", diagnosed "+str(diagnosed)+", cured: "+str(cured))
            for t in trials:
                succ = None
                if (t["start"] > diagnosed and (cured == None or t["start"] < cured)):
                    if(t["condition"] == condition["id"]):
                        succ = t["successful"]
                    #the trial is done when the patient has that condition
                    if(len(therapies)>0):
                        tl = therapies[-1][0].copy()
                        tl.append(t["therapy"])
                        therapies.append((tl, succ))
                    else:
                        therapies.append(([t["therapy"]], succ))
            # print(condition["id"])
            # print(therapies)
            ret[i][condition["id"]]=therapies
    return ret


dataset = readJson()
patients = createDataset(dataset)
# for i in range(0, len(patients)):
#     print("PATIENT "+str(i))
#     print(patients[i])
#     print("\n")


