from sys import platform
from datetime import datetime
import mysql.connector as mysql
import uuid
import random
import time
import string

# load firstnames
with open('first-names') as f:
    firstnames = [x.strip() for x in f.readlines()]

# load lastnames
with open('last-names') as f:
    lastnames = [x.strip() for x in f.readlines()]

# print (data)

def genUids(list):
    for i in range(0, 200):
        list.append(str(uuid.uuid4()))

personUids = []
ssns = []

for i in range(0, 200):
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

for i in range(0, 200):
    #dates.append(randomDate("1960-01-01", "1985-01-01", random.random()))
    dates.append(randomDate(1960, 1985, 1, 4, 1, 5))
    
deaths = []

for i in range(0, 200):
    chance = random.randint(0, 50)
    if (chance < 48):
        death = 0
    else:
        death = 1
    deaths.append(death);

genders = []

for i in range(0, 200):
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
sql = "DELETE FROM hospitalemployee; DELETE FROM patient; DELETE FROM person;"
output = cursor.execute(sql, multi=True)
db.commit()


# Insert person data
for i in range(0, 200):
    # print (personUids[i], data[i])
    sql = "insert into person (PersonUid, Active, FirstName, LastName, MiddleName, Ssn, BirthDate, DeceasedBool, Gender, Address) VALUES ('%s', 1, '%s', '%s', '%s', '%s', '%s', %i, '%s', '%s')" % (personUids[i], firstnames[random.randint(0, 4700)], lastnames[random.randint(0, 4700)], firstnames[random.randint(0, 4700)], ssns[i], dates[i], deaths[i], genders[i], addresses[i])
    output = cursor.execute(sql)
    db.commit()


cursor.execute("select PersonUid from person")

elgiblepat = []

i = 0
for row in cursor.fetchall():
    if (i == 150):
        break
    elgiblepat.append(row[0])
    i += 1

def genMRN():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

with open('conditions') as f:
    conds = [x.strip() for x in f.readlines()]

# Insert patient data
i = 0;
for patient in elgiblepat:
    sql = "insert into patient (PatientUid, MedicalRecordNumber, ArrivalDate, ReleaseDate, `Condition`) VALUES ('%s', '%s', '%s', '%s', '%s')" % (patient, genMRN(), randomDate(2012, 2012, 1, 3, 1, 2), randomDate(2012, 2012, 4, 5, 1, 2), conds[i])
    output = cursor.execute(sql)
    db.commit()
    i += 1

# Insert HEmployee data
cursor.execute("SELECT PersonUid FROM person WHERE PersonUid not in (select patient.PatientUid FROM patient)")
hemployees = cursor.fetchall()

with open('qualifications') as f:
    quals = [x.strip() for x in f.readlines()]

i = 0;
for e in hemployees:
    salary = int("%i%i%i%i%i.%i%i") % (random.randint(6, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9))
    sql = "insert into hospitalemployee (HEmployeeUid, Qualification, Salary) VALUES ('%s', '%s', %s)" % (e, quals[i], salary)
    print (sql)
    output = cursor.execute(sql)
    db.commit()
    i += 1

db.close()
