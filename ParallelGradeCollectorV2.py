import requests
from getpass import getpass
from bs4 import BeautifulSoup
import re
import threading
FALL_MODE = 1
SPRING_MODE = 2
SUMMER_MODE = 3
lock = threading.Lock()
session = requests.session()
indextest = 0

def printGrades(falls,springs,summers):
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
            totalH += int(su.split(":")[2].split("(")[1][0])
            totalPoints += int(su.split(":")[2].split("(")[1][0])*float(s.split(":")[2].split("(")[2].split(")")[0])
        print()
        print("GPA : " + str(round(totalPoints/totalH,2)))
        if(len(falls) == 0 and len(springs) == 0 and len(summers) == 0):
            print("GRADE NOT AVAILABLE YET")    

def checkmode(text,mode):
    if mode ==  FALL_MODE:
        if "Fall" in text:
            return True
        else:
            return False
    elif mode == SPRING_MODE:
        if "Spring" in text:
            return True
        else:
            return False
    else:
        if "Summer" in text:
            return True
        else:
            return False


def subjectInfo(head,session,falls,springs,summers):
    courseName = head.contents[0]
    retries = 0
    while True:
        try:
            r3 = session.get(head["href"])
            break
        except:
            retries+=1
            if retries >= 5:
                return
            continue
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


def login(mail,password):
    global session
    session = requests.session()
    url = 'https://eng.asu.edu.eg/login'
    login_data = dict()
    login_data["email"] = mail
    login_data["password"] = password
    x = session.get(url)
    print("Got to Login Page")
    soup = BeautifulSoup(x.text,features="html.parser")
    token = soup.find("input",{"name" : "_token"})["value"]
    login_data["_token"] = token
    r = session.post(url, data=login_data)
    print("Logged in!!!")

def getYear(year):
    r = session.get("https://eng.asu.edu.eg/dashboard/my_courses?years=" + year + "%2F" + str(int(year)+1) )
    print("Got the year")
    soup = BeautifulSoup(r.text,features="html.parser")
    a_all = soup.find_all("a")
    return a_all


def doIt(a_all,mode):           
    threads = []
    heads = []
    falls = []
    springs = []
    summers = []
    for i in a_all:
        if "committee" in str(i):
            heads.append(i)
    for head in heads:
        courseName = head.contents[0]
        if checkmode(courseName,mode) == True:
            thread = threading.Thread(target = subjectInfo,args = (head,session,falls,springs,summers))
            thread.start()
            threads.append(thread)
    for j in range(len(threads)):
        threads[j].join()
    printGrades(falls,springs,summers)


def getGrade():
    mail = input("Please enter your ID: ") + "@eng.asu.edu.eg"
    password = getpass("Please enter your password(don't worry the password you type is invisible): ")
    print()
    print("Example if you want 2023/2024, type 2023")
    print()
    year = input("Please Enter Academic Year: ")

    print()
    print("1 ---> displays courses of fall\n2 ---> displays courses of spring\n3 ---> displays courses of summer\n")
    mode = int(input("Please Enter the semester: "))
    while(True):
        #Try to Login (A New session is created for each login)
        while(True):
            try:
                login(mail,password)
                break
            except:
                print("Login failed retrying...")
                continue
        #Try to get year
        #If number of retries >= 10 retry the entire process
        num_retries = 0
        while(True):
            try:
                a_all = getYear(year)
                break
            except:
                if num_retries >= 10:
                    print("Max number of retries exceeded... ReDoing the whole process :(")
                    break
                num_retries+=1
                print("getYear failed retrying... Retries Count: ",num_retries)
                continue
        if num_retries >= 10:
            continue
        doIt(a_all,mode)   
        break

            
getGrade()

