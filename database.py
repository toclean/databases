import mysql.connector as mariadb
import uuid
import random

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
    firstdashflag = 0;
    for j in range(0, 9):
        if (firstdashflag == 0 and j == 3):
            firstdashflag = 1;
            rnums += "-"
        if (firstdashflag == 1 and j == 5):
            rnums += "-"
        rnums += str(random.randint(0, 9))
    ssns.append(rnums)

print (ssns)

# Create list of personUid
genUids(personUids)

with open('creds') as f:
    creds = [x.strip() for x in f.readlines()]

passwd = creds[0]

db = mariadb.connect(host="127.0.0.1", user="root", password=passwd, database="dbproject");

cursor = db.cursor()

for i in range(0, 200):
    # print (personUids[i], data[i])
    sql = "insert into person (PersonUid, Active, FirstName, LastName, MiddleName) VALUES ('%s', 1, '%s', '%s', '%s')" % (personUids[i], firstnames[random.randint(0, 4700)], lastnames[random.randint(0, 4700)], firstnames[random.randint(0, 4700)])
    # print (sql)
    output = cursor.execute(sql)
    # print (data)
    db.commit()

db.close()
