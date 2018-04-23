import mysql.connector as mariadb
import uuid

# load firstnames
with open('first-names') as f:
    data = [x.strip() for x in f.readlines()]

# print (data)

def genUids(list):
    for i in range(0, 200):
        list.append(str(uuid.uuid4()))

personUids = []

# Create list of personUids
genUids(personUids)

with open('creds') as f:
    creds = [x.strip() for x in f.readlines()]

passwd = creds[0]

db = mariadb.connect(host="127.0.0.1", user="root", password=passwd, database="dbproject");


cursor = db.cursor()

for i in range(0, 200):
    print (personUids[i], data[i])
    sql = "insert into person (PersonUid, Active, FirstName) VALUES ('%s', 1, '%s')" % (personUids[i], data[i])
    print (sql)
    data = cursor.execute(sql)
    # print (data)
    db.commit()

db.close()
