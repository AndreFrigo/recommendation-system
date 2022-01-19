from utils import readJson, createDataset, therapyList
import random
import copy

##test
#remove one therapy T from patient P and condition C, then try to guess the therapy
#optional arguments: simScore score for user similarity, succScore: score for succession rate (simScore + succScore = 1), seed: seed for random function
def test(patients, numTests, simScore = 0.3, succScore = 0.7, seed = None):
    if(seed != None):
        random.seed(seed)
    i = 0
    correct = 0
    while (i<numTests):
        #select a random patient
        pid = random.randint(0, len(patients)-1)
        #select a random condition for that patient
        if(len(patients[pid]) > 0):
            cond = random.choice([elem for elem in patients[pid]])
            if(len(patients[pid][cond]) > 0):
                #remove the last therapy taken for that condition and try to guess it (only for already cured conditions)
                elem = patients[pid][cond][-1]
                if(elem[1] == 100):
                    print("TEST: EXECUTION "+str(i))
                    # print("PatientID: "+str(pid)+", condition: "+str(cond)+", therapies done: "+str(patients[pid][cond]))
                    patients[pid][cond].remove(elem)
                    tl = therapyList(patients, pid, cond, simScore, succScore)
                    for ti in range(0, len(tl)):
                        # print("Checking "+str(tl[ti][1]+" with "+str(elem[0][-1])))
                        if(tl[ti][1] == elem[0][-1]):
                            #the correct therapy is inside the 5 suggested
                            correct += 1
                    patients[pid][cond].append(elem)
                else:
                    i -= 1
            else:
                i -= 1
        else:
            i -= 1
        i += 1
    print("CORRECT: "+str(correct)+"/"+str(numTests))
    return correct/numTests
