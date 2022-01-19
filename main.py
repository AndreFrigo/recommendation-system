from utils import readJson, createDataset, therapyList
from test import test
import sys

#get therapy name given input dataset and therapy ID
def getTherapyName(dataset, therapyID):
    for e in dataset["Therapies"]:
        if(e["id"] == therapyID):
            return e["name"]

#in the data structure are used the conditions kind, but input is condition id, this function gives the condition kind given the condition id
def getConditionKind(dataset, conditionID):
    for p in dataset["Patients"]:
        for c in p["conditions"]:
            if ( c["id"] == conditionID):
                return c["kind"]

if(len(sys.argv) == 4):
    inputDataset = str(sys.argv[1])
    inputPatient = int(sys.argv[2])
    inputCondition = str(sys.argv[3])

    # print("Start script with patientID: "+str(inputPatient)+", conditionID: "+str(inputCondition))
    #Read json dataset
    dataset = readJson(inputDataset)
    # print("Done reading dataset")
    #Create patients list
    patients = createDataset(dataset)
    # print("Done creating data structure")

    #find the condition kind from the condition id
    cond = getConditionKind(dataset, inputCondition)
    #compare with the other patients and get an ordered list of patients based on similarity
    tl = therapyList(patients, inputPatient, cond)
    #create the list to print
    ret = [(e[1], getTherapyName(dataset, e[1])) for e in tl]
    print("INPUT: "+str(inputPatient)+" "+str(inputCondition))
    print("OUTPUT: "+str(ret))

    
    # #This is how to test
    # scores = [(0.3, 0.7)]
    # res = []
    # for elem in scores:
    #     print("Test with scores: "+str(elem))
    #     t1 = test(patients, 50, elem[0], elem[1], seed=5)
    #     t2 = test(patients, 50, elem[0], elem[1], seed=10)
    #     t3 = test(patients, 50, elem[0], elem[1], seed=15)
    #     res.append((elem, (t1+t2+t3)/3))
    # print("RES: "+str(res))


else:
    print("Format error, run the program passing: dataset.json PatientID conditionID")




    


