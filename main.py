from utils import readJson, createDataset, therapyList
from test import test
import sys

#get therapy name given input dataset and therapy ID
def getTherapyName(dataset, therapyID):
    for e in dataset["Therapies"]:
        if(e["id"] == therapyID):
            return e["name"]


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
    #compare with the other patients and get an ordered list of patients based on similarity
    tl = therapyList(patients, inputPatient, inputCondition)
    #create the list to print
    ret = [(e[1], getTherapyName(dataset, e[1])) for e in tl]
    print(ret)

    
    #This is how to test
    # scores = [(0.3, 0.7), (0.35, 0.65), (0.45, 0.55), (0.5, 0.5)]
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




    


