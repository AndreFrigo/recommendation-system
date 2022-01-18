from utils import readJson, createDataset, therapyList
import random
import copy

##test
#remove one therapy T from patient P and condition C, then try to guess the therapy
#optional arguments: simScore score for user similarity, succScore: score for succession rate (simScore + succScore = 1), seed: seed for random function
def test(patients, numTests, simScore = 0.25, succScore = 0.75, seed = None):
    if(seed != None):
        random.seed(seed)

    #2: 14/100
    score = 0
    num = 0
    i = 0
    correct = 0
    while (i<numTests):
        #select a random patient
        pid = random.randint(0, len(patients))
        #select a random condition for that patient
        if(len(patients[pid]) > 0):
            cond = random.choice([elem for elem in patients[pid]])
            if(len(patients[pid][cond]) > 0):
                #remove the last therapy taken for that condition and try to guess it (only for already cured conditions)
                elem = patients[pid][cond][-1]
                if(elem[1] == 100):
                    print("TEST: EXECUTION "+str(i))
                    print("PatientID: "+str(pid)+", condition: "+str(cond)+", therapies done: "+str(patients[pid][cond]))
                    print("Removing "+str(elem))
                    patients[pid][cond].remove(elem)
                    tl = therapyList(patients, pid, cond, simScore, succScore)
                    print("Predicted: "+str([e[1] for e in tl]))
                    oldnum = num
                    for ti in range(0, len(tl)):
                        # print("Checking "+str(tl[ti][1]+" with "+str(elem[0][-1])))
                        if(tl[ti][1] == elem[0][-1]):
                            #the therapy correct therapy is inside the 5 suggested
                            #the score is: position number * |actual success - predicted success| 
                            #the objective is minimizing this value (predicting the wrong therapy gives the max value= 5*100),
                            #predicting the right therapy as first is better because the factor is lower
                            #TODO
                            # score += abs(tl[ti][2] - elem[1]) * ti
                            score += ti
                            num += 1
                            correct += 1
                            print("OK: pos: "+str(ti)+", error: "+str(abs(tl[ti][2] - elem[1])))
                    if (oldnum == num):
                        #the correct therapy has not been predicted
                        #score += 500
                        #TODO
                        score += 10
                        num += 1
                        print("WRONG")
                    patients[pid][cond].append(elem)
                    print("\n----------------------------------------------------------------------------------------------------------------\n")
                else:
                    i -= 1
            else:
                i -= 1
        else:
            i -= 1
        i += 1
    print("CORRECT: "+str(correct)+"/"+str(numTests))
    return correct/numTests
