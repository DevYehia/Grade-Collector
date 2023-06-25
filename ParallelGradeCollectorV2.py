import requests
from getpass import getpass
from bs4 import BeautifulSoup
import re
import threading
lock = threading.Lock()
session = requests.session()
def subjectInfo(head,session,falls,springs,summers):
    r3 = session.get(head["href"])
    courseName = head.contents[0]
    soup3 = BeautifulSoup(r3.text,features="html.parser")
    lis= soup3.find_all("li")
    bs= soup3.find_all("b")
    creditH = None
    for k in bs:
        if "Credit" in str(k):
            creditH = k.contents[0]
    for j in lis:
        if re.search("[ABCDF][+-]*\s",str(j.contents[0])) and len(j.contents[0]) <= 20:
            #lock.acquire()
            if "Fall" in courseName:
                falls.append(courseName + ": " + creditH + ' Grade ' + j.contents[0])
            elif "Spring" in courseName:
                springs.append(courseName + ": " + creditH + ' Grade ' + j.contents[0])
            else:
                summers.append(courseName + ": " + creditH + ' Grade ' + j.contents[0])
            #lock.release()
url = 'https://eng.asu.edu.eg/login'
x = session.get(url)
soup = BeautifulSoup(x.text,features="html.parser")
token = soup.find("input",{"name" : "_token"})["value"]
login_data = dict()
login_data["_token"] = token
login_data["email"] = str(input("Please enter your ID: ")) + "@eng.asu.edu.eg"
login_data["password"] = getpass("Please enter your password: ")
print("Example : 1 ---> displays courses of first year")
startYear = input("Please Enter Academic Year Number: ")
r = session.post(url, data=login_data)
r = session.get("https://eng.asu.edu.eg/dashboard/my_courses")
soup = BeautifulSoup(r.text,features="html.parser")
option_all = soup.find_all("option")
startYear = option_all[len(option_all)-int(startYear)]["value"].split("/")[0]

r = session.get("https://eng.asu.edu.eg/dashboard/my_courses?years=" + startYear + "%2F" + str(int(startYear)+1) )
soup = BeautifulSoup(r.text,features="html.parser")
a_all = soup.find_all("a")
threads = []
heads = []
falls = []
springs = []
summers = []
for i in a_all:
    if "committee" in str(i):
        heads.append(i)
for i in heads:
    thread = threading.Thread(target = subjectInfo,args = (i,session,falls,springs,summers))
    thread.start()
    threads.append(thread)
for j in range(len(threads)):
    threads[j].join()
totalH = 0
totalPoints = 0
if (len(falls) != 0):
    print("---------Fall Courses---------")
    for f in falls:
        print(f)
        totalH += int(f.split(":")[2].split("(")[1][0])
        totalPoints += int(f.split(":")[2].split("(")[1][0])*float(f.split(":")[2].split("(")[2].split(")")[0])
    print()
    print("GPA : " + str(round(totalPoints/totalH,2)))
totalH = 0
totalPoints = 0
if (len(springs) != 0):
    print("---------Spring Courses---------")
    for s in springs:
        print(s)
        totalH += int(s.split(":")[2].split("(")[1][0])
        totalPoints += int(s.split(":")[2].split("(")[1][0])*float(s.split(":")[2].split("(")[2].split(")")[0])
    print()
    print("GPA : " + str(round(totalPoints/totalH,2)))
totalH = 0
totalPoints = 0
if (len(summers) != 0):
    print("---------Summer Courses---------")
    for su in summers:
        print(su)
        print(s)
        totalH += int(su.split(":")[2].split("(")[1][0])
        totalPoints += int(su.split(":")[2].split("(")[1][0])*float(s.split(":")[2].split("(")[2].split(")")[0])
    print()
    print("GPA : " + str(round(totalPoints/totalH,2)))