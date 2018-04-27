from sys import platform
from datetime import datetime, timedelta
if (platform == "linux" or platform == "linux2"):
    import mysql.connector as mariadb
else:
    import mysql.connector as mysql
import uuid
import random
import time
import string
import math

numPersons = 1000
numPatients = .60 * numPersons # 600
numHEmployees = .40 * numPersons # 400
numDocs = .25 * numHEmployees # 100
numNurses = .50 * numHEmployees # 200
numPEmployees = .25 * numHEmployees # 100


numPTech = .75 * numPEmployees # 75
numPharm = .25 * numPEmployees # 25
numPatientsPerRoom = 3
numMedication = numPersons

# load firstnames
with open('first-names') as f:
    firstnames = [x.strip() for x in f.readlines()]

# load lastnames
with open('last-names') as f:
    lastnames = [x.strip() for x in f.readlines()]

# print (data)

def genUids(list):
    for i in range(0, numPersons):
        list.append(str(uuid.uuid4()))

personUids = []
ssns = []

for i in range(0, numPersons):
    rnums = ""
    firstdashflag = 0
    for j in range(0, 9):
        if (firstdashflag == 0 and j == 3):
            firstdashflag = 1
            rnums += "-"
        if (firstdashflag == 1 and j == 5):
            rnums += "-"
        rnums += str(random.randint(0, 9))
    ssns.append(rnums)

# print (ssns)

# Create list of personUid
genUids(personUids)

# generate random birthdates
def randomDate(sYear, eYear, sMonth, eMonth, sDay, eDay):
    year = random.randint(sYear, eYear)
    month = random.randint(sMonth, eMonth)
    day = random.randint(sDay, eDay)
    return datetime(year, month, day)

dates = []

for i in range(0, numPersons):
    #dates.append(randomDate("1960-01-01", "1985-01-01", random.random()))
    dates.append(randomDate(1960, 1985, 1, 4, 1, 5))
    
deaths = []

for i in range(0, numPersons):
    chance = random.randint(0, 50)
    if (chance < 48):
        death = 0
    else:
        death = 1
    deaths.append(death)

genders = []

for i in range(0, numPersons):
    chance = random.randint(0, 10)
    if (chance <= 5):
        genders.append("Male")
    else:
        genders.append("Female")

with open('street-addresses') as f:
    addresses = [x.strip() for x in f.readlines()]

with open('creds') as f:
    creds = [x.strip() for x in f.readlines()]

passwd = creds[0]

if (platform == "linux" or platform == "linux2"):
    db = mariadb.connect(host="127.0.0.1", user="root", password=passwd, database="dbproject")
else:
    db = mysql.connect(host='127.0.0.1', user='root', passwd=passwd, db='dbproject')

cursor = db.cursor()

# delete previous entries
sql = "DELETE FROM NURSE"
output = cursor.execute(sql, multi=True)
db.commit()


# Insert person data
for i in range(0, numPersons):
    # print (personUids[i], data[i])
    sql = "insert into person (PersonUid, Active, FirstName, LastName, MiddleName, Ssn, BirthDate, DeceasedBool, Gender, Address) VALUES ('%s', 1, '%s', '%s', '%s', '%s', '%s', %i, '%s', '%s')" % (personUids[i], firstnames[random.randint(0, 4700)], lastnames[random.randint(0, 4700)], firstnames[random.randint(0, 4700)], ssns[i], dates[i], deaths[i], genders[i], addresses[random.randint(0, 200)])
    output = cursor.execute(sql)


cursor.execute("select PersonUid from person")

elgiblepat = []

i = 0
for row in cursor.fetchall():
    if (i == numPatients):
        break
    elgiblepat.append(row[0])
    i += 1

def genMRN():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

with open('conditions') as f:
    conds = [x.strip() for x in f.readlines()]

# Insert patient data
i = 0
for patient in elgiblepat:
    sql = "insert into patient (PatientUid, MedicalRecordNumber, ArrivalDate, ReleaseDate, `Condition`) VALUES ('%s', '%s', '%s', '%s', '%s')" % (patient, genMRN(), randomDate(2012, 2012, 1, 3, 1, 27), randomDate(2012, 2012, 3, 4, 1, 30), conds[random.randint(0, 200)])
    output = cursor.execute(sql)
    i += 1

# Insert HEmployee data
cursor.execute("SELECT PersonUid FROM person WHERE PersonUid not in (select patient.PatientUid FROM patient)")
hemployees = cursor.fetchall()

with open('qualifications') as f:
    quals = [x.strip() for x in f.readlines()]

i = 0
for e in hemployees:
    salary = "%i%i%i%i%i.%i%i" % (random.randint(6, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9))
    sql = "insert into hospitalemployee (HEmployeeUid, Qualification, Salary) VALUES ('%s', '%s', %d)" % (e[0], quals[random.randint(0, 79)], float(salary))
    output = cursor.execute(sql)
    i += 1

cursor.execute("SELECT HEmployeeUid FROM hospitalemployee LIMIT %d" % numDocs)
doctorData = cursor.fetchall()

def genNum(x):
    nums = ""
    for i in range(1,x):
        nums += str(random.randint(1,9))
    return nums

for doctor in doctorData:
    sql = "insert into doctor (DoctorUid, NpiNumber, DEANumber) VALUES ('%s', '%s', '%s')" % (doctor[0], genNum(10), genNum(7))
    output = cursor.execute(sql)

cursor.execute("SELECT HEmployeeUid FROM hospitalemployee WHERE HEmployeeUid NOT IN (SELECT DoctorUid FROM doctor) LIMIT %d" % numNurses)
nurseData = cursor.fetchall()

nurses = []

for nurse in nurseData:
    nurses.append(nurse[0])

i = 0
j = 1
for z in range(0, len(doctorData)):
    sql = "insert into nurse (NurseUid, DoctorUid, PatientCount) VALUES ('%s', '%s', '%s')" % (nurses[i], doctorData[z][0], numPatientsPerRoom)
    cursor.execute(sql)
    sql = "insert into nurse (NurseUid, DoctorUid, PatientCount) VALUES ('%s', '%s', '%s')" % (nurses[j], doctorData[z][0], numPatientsPerRoom)
    cursor.execute(sql)
    i += 2
    j += 2

cursor.execute("SELECT PersonUid FROM person WHERE PersonUid not in (SELECT DoctorUid FROM doctor) and PersonUid not in (SELECT NurseUid FROM nurse) and PersonUid not in (SELECT PatientUid FROM patient)")
peDate = cursor.fetchall()

pharmsmep = []

for pe in peDate:
    pharmsmep.append(pe[0])

for i in range(0, len(pharmsmep)):
    sql = "insert into pharmacy_employee (PEmployeeUid) VALUES ('%s')" % (pharmsmep[i])
    cursor.execute(sql)

cursor.execute("SELECT PEmployeeUid FROM pharmacy_employee LIMIT %s" % int(numPharm))
pemp = cursor.fetchall()

pharm = []

for pe in pemp:
    pharm.append(pe[0])

for p in pharm:
    sql = "insert into pharmacist (PharmacistUid, DEANumber) VALUES ('%s', '%s')" % (p, genNum(7))
    cursor.execute(sql)

cursor.execute("SELECT PEmployeeUid FROM pharmacy_employee WHERE PEmployeeUid not in (SELECT PharmacistUid FROM pharmacist)")
premain = cursor.fetchall()

techs = []

for p in premain:
    techs.append(p[0])

pharmtech = []

# insert pharmtech data
for i in range(0, len(pharm)):
    for j in range(0, int(math.ceil(len(techs)/len(pharm)))):
        pharmtech.append(pharm[i])

for i in range(0, len(techs)):
    sql = "insert into pharmacy_technician (PTechUid, ManagerUid) VALUES ('%s', '%s')" % (techs[i], pharmtech[i])
    cursor.execute(sql)


# insert hospital data
cursor.execute("insert into hospital (HospitalUid, NumberOfRooms) VALUES ('%s', '%s')" % (uuid.uuid4(), numNurses))

types = ["Surgery", "Testing", "Nursing", "ICU", "Severe", "Stable"]

# insert data for rooms
for i in range(0, int(math.ceil(numNurses))):
    cursor.execute("insert into room (RoomUid, RoomNumber, Occupied, RoomType, NumberOfBeds) VALUES ('%s', '%s', '%s', '%s', '%s')" % (uuid.uuid4(), i+1, 1, types[random.randint(0, len(types) - 1)], 5))

# insert data for pharmacy
for i in range(0, int(numPEmployees / 50)):
    cursor.execute("insert into pharmacy (PharmacyUid) VALUES ('%s')" % uuid.uuid4())

# get medication names
with open('medication-names') as f:
    meds = [x.strip() for x in f.readlines()]

with open('medication-descriptions') as f:
    desc = [x.strip() for x in f.readlines()]

method = ["Oral", "Intravenous"]

# insert data for medication
for i in range(0, numMedication):
    start = datetime.now()#datetime.strptime("%Y-%d-%m")
    end = start + timedelta(days=random.randint(0, 60))
    cursor.execute("insert into medication (MedicationUid, Name, Code, Start, End, Units_Per_Day, Description, Dosage, Method) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', \"%s\", '%s', '%s')" % (uuid.uuid4(), meds[random.randint(0, len(meds) - 1)], genNum(8), start, end, random.randint(1, 4), desc[random.randint(0, len(desc) - 1)], str(random.randint(25, 300)) + "mg", method[random.randint(0, 1)]))

cursor.execute("SELECT MedicationUid FROM medication")
meds = cursor.fetchall()

medarry = []

for i in meds:
    medarry.append(meds[0])


cursor.execute("SELECT PharmacyUid FROM pharmacy")
pharms = cursor.fetchall()

pharmsarry = []

for pharm in pharms:
    pharmsarry.append(pharm[0])

maintains = []

for i in range(0, len(pharmsarry)):
    for j in range(0, int(math.ceil(len(medarry)/len(pharmsarry)))):
        maintains.append(pharmsarry[i])

# insert data for pharmaceutical_supplies
for med in meds:
    cursor.execute("insert into pharmaceutical_supplies (MedicationUid, Quantity, Cost_Per_Unit, Reorder_Amount) VALUES ('%s', '%s', '%s', '%s')" % (med[0], str(random.randint(0, 400)) + "g", str(round(random.uniform(25,1000), 2)), random.randint(25, 300)))

for i in range(0, len(meds)):
    sql = "insert into maintains (MedicationUid, PharmacyUid) VALUES ('%s', '%s')" % (meds[i][0], maintains[i])
    cursor.execute(sql)

pharmacy_works_for = []

for i in range(0, len(pharmsarry)):
    for j in range(0, int(math.ceil(len(pharmsmep)/len(pharmsarry)))):
        pharmacy_works_for.append(pharmsarry[i])

for i in range(0, len(pharmacy_works_for)):
    sql = "insert into pharmacy_works_for (PEmployeeUid, PharmacyUid) VALUES ('%s', '%s')" % (pharmsmep[i], pharmacy_works_for[i])
    cursor.execute(sql)

cursor.execute("SELECT PTechUid, ManagerUid FROM pharmacy_technician")

for tech in cursor.fetchall():
    cursor.execute("insert into pharmacist_oversees (PTechUid, PharmacistUid) VALUES ('%s', '%s')" % (tech[0], tech[1]))

cursor.execute("SELECT NurseUid, DoctorUid FROM nurse")

for nurse in cursor.fetchall():
    cursor.execute("insert into advises (NurseUid, DoctorUid) VALUES ('%s', '%s')" % (nurse[0], nurse[1]))

cursor.execute("SELECT HospitalUid FROM hospital")

hosuid = cursor.fetchall()[0]

for e in hemployees:
    cursor.execute("insert into hospital_works_for (HEmployeeUid, HospitalUid) VALUES ('%s', '%s')" % (e[0], hosuid[0]))

cursor.execute("SELECT RoomUid FROM ROOM")

for room in cursor.fetchall():
    cursor.execute("insert into has (RoomUid, HospitalUid) VALUES ('%s', '%s')" % (room[0], hosuid[0]))

cursor.execute("SELECT DoctorUid FROM doctor")

doctors = []

for doc in cursor.fetchall():
    doctors.append(doc[0])

prescribes = []

for i in range(0, len(doctors)):
    for j in range(0, int(math.ceil(len(medarry)/len(doctors)))):
        prescribes.append(doctors[i])

for i in range(0, len(prescribes)):
    cursor.execute("insert into prescribes (MedicationUid, DoctorUid) VALUES ('%s', '%s')" % (meds[i][0], prescribes[i]))

cursor.execute("SELECT NurseUid, DoctorUid FROM advises")

nurses = []
for n in cursor.fetchall():
    nurses.append([n[0], n[1]])

nursesadj = []

for i in range(0, len(nurses)):
    for j in range(0, 3):
        nursesadj.append([nurses[i][0], nurses[i][1]])

cursor.execute("SELECT PatientUid FROM patient")

i = 0
for patient in cursor.fetchall():
    cursor.execute("insert into doctor_oversees (PatientUid, NurseUid, DoctorUid) VALUES ('%s', '%s', '%s')" % (patient[0], nursesadj[i][0], nursesadj[i][1]))
    i += 1

cursor.execute("SELECT PTechUid from pharmacy_technician")
pt = []

for p in cursor.fetchall():
    pt.append(p[0])

ptadj = []

for i in range(0, len(pt)):
    for j in range(0, 8):
        ptadj.append(pt[i])

cursor.execute("SELECT * FROM patient")

i = 0
for p in cursor.fetchall():
    cursor.execute("insert into retrieves_medication_from (PatientUid, MedicationUid, PTechUid) VALUES ('%s', '%s', '%s')" % (p[0], medarry[i][0], ptadj[i]))
    i += 1

db.commit()

db.close()
