from sys import platform
from datetime import datetime
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
numDocs = .05 * numPersons
numNurses = .1 * numPersons
numPEmployees = .1 * numPersons
numHEmployees = .25 * numPersons
numPatients = .75 * numPersons
numPTech = .75 * numPEmployees
numPharm = .25 * numPEmployees

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
    sql = "insert into nurse (NurseUid, DoctorUid, PatientCount) VALUES ('%s', '%s', '%s')" % (nurses[i], doctorData[z][0], 5)
    cursor.execute(sql)
    sql = "insert into nurse (NurseUid, DoctorUid, PatientCount) VALUES ('%s', '%s', '%s')" % (nurses[j], doctorData[z][0], 5)
    cursor.execute(sql)
    i += 2
    j += 2

cursor.execute("SELECT PersonUid FROM person WHERE PersonUid not in (SELECT DoctorUid FROM doctor) and PersonUid not in (SELECT NurseUid FROM nurse) and PersonUid not in (SELECT PatientUid FROM patient)")
peDate = cursor.fetchall()

pharms = []

for pe in peDate:
    pharms.append(pe[0])

for i in range(0, len(pharms)):
    sql = "insert into pharmacy_employee (PEmployeeUid) VALUES ('%s')" % (pharms[i])
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
    for j in range(0, math.ceil(len(techs)/len(pharm))):
        pharmtech.append(pharm[i])

for i in range(0, len(techs)):
    sql = "insert into pharmacy_technician (PTechUid, ManagerUid) VALUES ('%s', '%s')" % (techs[i], pharmtech[i])
    cursor.execute(sql)

# print (pharmtech[0], pharmtech[1])



db.commit()

db.close()
