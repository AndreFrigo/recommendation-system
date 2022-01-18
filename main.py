from utils import readJson, createDataset, therapyList
from test import test


#Read json dataset
dataset = readJson()
print("1")
#Create patients list
patients = createDataset(dataset)
print("2")
#compare with the other patients and get an ordered list of patients based on similarity



# # #first test case, Patient 6, condition 248
# print(therapyList(patients, 6, "Cond248"))
# print("3")

scores = [(0.3, 0.7), (0.35, 0.65), (0.45, 0.55), (0.5, 0.5)]
res = []
for elem in scores:
    print("Test with scores: "+str(elem))
    t1 = test(patients, 50, elem[0], elem[1], seed=5)
    t2 = test(patients, 50, elem[0], elem[1], seed=10)
    t3 = test(patients, 50, elem[0], elem[1], seed=15)
    res.append((elem, (t1+t2+t3)/3))

print("RES: "+str(res))


    


