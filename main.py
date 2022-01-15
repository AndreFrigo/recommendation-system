from utils import readJson, createDataset, therapyList



#Read json dataset
dataset = readJson()
print("1")
#Create patients list
patients = createDataset(dataset)
print("2")
#compare with the other patients and get an ordered list of patients based on similarity



# #first test case, Patient 6, condition 248
print(therapyList(patients, 6, "Cond248"))
print("3")
