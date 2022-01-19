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

            #sort the therapies by their start date
            therapies.sort(key=lambda x: x[2])
            #store only yhe important values, I'm not interested on the date anymore, just the order
            th = []
            for j in range(0, len(therapies)):
                th.append([therapies[j][0], therapies[j][1]])
            #create all the possible groups of therapies, for example (th1, th2, th3) becomes ([th1], [th1,th2], [th1,th2,th3]) to store causality
            therapies = []
            for j in range(0, len(th)):
                if(j==0):
                    therapies.append([[th[0][0]], th[0][1]])
                else:
                    previous = [x for x in therapies[j-1][0]]
                    previous.append(th[j][0])
                    therapies.append([previous, th[j][1]])
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
    for condition in ret:
        for trial in ret[condition]:
            if(trial[1] != None):
               trial[1] -= tot
    return ret

#longest common subsequence between two lists
#if getList == False it returns just the length of the lcs, otherwise it returns the list of lcs, if getBoth == True it returns both
def lcs(a, b, getList = False, getBoth = False):
    a_len = len(a)
    b_len = len(b)
    dp = []
    for i in range(a_len + 1):
        dp.append([0 for j in range(b_len + 1)])
    for i in range(1, a_len + 1):
        for j in range(1, b_len + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j - 1])
    max_length = dp[a_len][b_len]
    if(getBoth == False):
        if(getList == False):
            return max_length
        else:
            return lcs_list(a, b, dp, a_len, b_len)
    else:
        return(max_length, lcs_list(a, b, dp, a_len, b_len))

#function needed inside lcs
def lcs_list(a, b, dp, i, j):
    if i == 0 or j == 0:
        return []
    if a[i-1] == b[j-1]:
        ret = lcs_list(a, b, dp, i-1, j-1)
        ret.append(a[i-1])
        return ret
    else:
        if dp[i-1][j] > dp[i][j-1]:
            ret = lcs_list(a, b, dp, i-1, j)
            return ret
        else:
            ret = lcs_list(a, b, dp, i, j-1)
            return ret


#compare one sequence of trials (trial1) of one patient with all the sequences of trials for one specific condition of an other patient
#based on LCS to keep the order information, normalized over the length of the longest element between the two trials of the patients
#returns the similarity value and the success rate of the second patient for the most similar trial 
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
            sim = lcs(trial1, elem[0])
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
            # el2 share some conditions with el1, check the therapies
            for trial in el1[condition]:
                if(trial[1] != None):
                    sim = compareTrials(trial[0], el2[condition])
                    if sim[0] != 0:
                        if condition in common:
                            common[condition].append(trial[0])
                        else:
                            common[condition] = [trial[0]]
                        #the same therapy list has been applied between the two
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
    
#compare the patient with ID:patientID with all the other patients, 
#return a list of tuples (patient id, similarity value) ordered in decreasing order by the similarity value [-1;1]
def similarPatients(patientID, patients):
    similarPatients = []
    p = normalizePatient(patients[patientID])
    for i in range(0, len(patients)):
        if(i!=patientID):
            sim = pearsonCorrelation(p, patients[i])
            similarPatients.append((i, sim))
    return sorted(similarPatients, key=lambda x: x[1], reverse=True)


#suggest the therapy to take in order to try to solve the condition
#input: therapyList (list of therapies done trying to solve the condition), condition (the condition id), patient2 (the patient to use to guess the therapy)
#returns a tuple (therapy, success), where therapy is the therapy id and success the success rate for that therapy (considering the previous therapies done)
def suggestTherapy(therapyList, condition, patient2):
    #list of trials done by patient2 to try to solve the condition
    tl = patient2[condition]
    #get the last element and check if the successfull rate is known
    l = len(tl)
    stop = False
    while(l >= 0 and stop == False):
        l -= 1
        #in case of no therapies applied the list is empty, in this case return None
        try:
            succ = tl[l][1]
        except:
            return None
        if(succ != None):
            stop = True
    #tl[l] contains one list of trials with the last success rate != None
    while (stop == True):
        # l contains the index of the last meaningful set of trials
        # compare the trials made by the two patients
        numTrials = len(tl[l][0])
        if (numTrials > 1):
            #The doctor can suggest just one therapy to take
            common = lcs(therapyList, tl[l][0], getBoth=True)
            if(numTrials - common[0] == 1):
                #it has to be as following: COMMON_THERAPIES, THx
                #where COMMON_THERAPIES are the therapies that both patients had in the same order and THx is the therapy that patient2 did after the therapies in common
                ok = True
                for i in range(0, numTrials):
                    if(i != numTrials-1):
                        #check if the therapies are the same
                        if(tl[l][0][i] != therapyList[i]):
                            ok = False
                    else:
                        #found the therapy, return its id and success rate
                        if (ok==True):
                            if(tl[l][1] != None):
                                return (tl[l][0][i], tl[l][1])
                            else:
                                return None
                        else:
                            return None
            else:
                #look for the trial before
                if(l==0):
                    return None
                l -= 1
            
        else:
            #numTrials = 1, just suggest the therapy taken 
            if(tl[l][1] != None):
                return (tl[l][0][0], tl[l][1])
            else: 
                return None
    return None

#function used inside therapyList
# gives the score for a specific tuple (User similarity, therapy suggested, success rate) to decide which therapies to use
def scoreSuggestion(suggestion, sim, succ):
    #It is used the successRate in the interval [0,1] and the userSimilarity in the interval [-1,1]
    userSimilarity = suggestion[0]
    successRate = suggestion[2]/100
    return sim*userSimilarity + succ*successRate



#given all the patients, one patient id and condition id, get the list of possible therapies to apply, with the success rate and user similarity
#optional arguments: simScore score for user similarity, succScore: score for succession rate (simScore + succScore = 1)
#return (User similarity, therapy suggested, success rate)
def therapyList(patients, patientID, conditionID, simScore = 0.3, succScore = 0.7):
    #patients ordered by similarity, each element is (patient id, similarity value)
    sim = similarPatients(patientID, patients)
    #ordered list of all the therapies done by that user for that specific condition
    therapies = patients[patientID][conditionID][-1][0] if len(patients[patientID][conditionID]) > 0 else []
    #list of therapy to suggest
    tl = []
    i=0
    for elem in sim:
        pid = elem[0]
        if (conditionID in patients[pid]):
            th = suggestTherapy(therapies, conditionID, patients[pid])
            if(th != None):
                tl.append((elem[1], th[0], th[1]))
    
    #sort the therapies based on user similarity and success rate
    completeList = sorted(tl, key=lambda x: scoreSuggestion(x, simScore, succScore), reverse=True)
    # return the first 5 therapyIDs (no duplicates)
    ret = []
    while(len(ret)<5 and i<len(completeList)):
        if(completeList[i] not in ret):
            ret.append(completeList[i])
        i+=1
    return ret
