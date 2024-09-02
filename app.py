import streamlit as st

import re
import threading
import pandas as pd
from Login import *
import datetime

# Constants for semester modes

FALL_MODE = 1
SPRING_MODE = 2
SUMMER_MODE = 3

# Initialize session state
if 'session' not in st.session_state:
    st.session_state.session = None

if 'grades' not in st.session_state:
    st.session_state.grades = []

def printGrades(Semester,mode):
    grades_list = []
    hours_list = []
    names_list = []
    codes_list = []
    def calculateGPA(courses):
        totalH = 0
        totalPoints = 0
        for course in courses:
            #totalH += int(course.split(":")[2].split("(")[1][0])
            #st.write(course)
            course_data = course.split("$")  # course, creditH, grade
            codes_list.append(course_data[0].split(":")[0])
            names_list.append(course_data[0].split(":")[1])
            #st.write(course_data)
            course_hour = int(course_data[1].split("(")[1][0])
            grades_list.append(course_data[2])
            hours_list.append(course_hour)
            totalH += course_hour
            try:
                #totalPoints += int(course.split(":")[2].split("(")[1][0]) * float(course.split(":")[2].split("(")[2].split(")")[0])
                
                totalPoints += int(course_data[1].split("(")[1][0]) * float(course_data[2].split("(")[1].split(")")[0])
            except:
                totalPoints += 0
        return round(totalPoints / totalH, 2) if totalH != 0 else 0


    if Semester:
        if mode ==1:
            st.subheader(f"**Fall GPA:** {calculateGPA(Semester)}")
        if mode ==2:
            st.subheader(f"**Spring GPA:** {calculateGPA(Semester)}")
        if mode==3:
            st.subheader(f"**Summer GPA:** {calculateGPA(Semester)}")

        df = pd.DataFrame({
                "Course Code": codes_list,
                "Course Name": names_list,
                "Credit Hours": hours_list,
                "Grade": grades_list
                        },index=None)
        
        #df = pd.DataFrame(grades_data, columns=['Course'],index=None)
        st.table(df)
    else:

        st.error("**GRADE NOT AVAILABLE YET**")
        
    

def checkmode(text, mode):
    if mode == FALL_MODE:
        return "Fall" in text
    elif mode == SPRING_MODE:
        return "Spring" in text
    else:
        return "Summer" in text

def subjectInfo(head, session, falls, springs, summers):
    courseName = head.contents[0]
    retries = 0
    while True:
        try:
            r3 = session.get(head["href"])
            break
        except:
            retries += 1
            if retries >= 5:
                return
            continue

    soup3 = BeautifulSoup(r3.text, features="html.parser")
    lis = soup3.find_all("li")
    bs = soup3.find_all("b")
    creditH = None
    for k in bs:
        if "Credit" in str(k):
            creditH = k.contents[0]

    for j in lis:
        if re.search("[ABCDF][+-]*\s", str(j.contents[0])) and len(j.contents[0]) <= 20:
            if "Fall" in courseName:
                falls.append(courseName + "$ " + creditH + '$ ' + j.contents[0])
            elif "Spring" in courseName:
                springs.append(courseName + "$ " + creditH + '$ ' + j.contents[0])
            else:
                summers.append(courseName + "$ " + creditH + '$ ' + j.contents[0])



def getYear(session, year):
    r = session.get(f"https://eng.asu.edu.eg/dashboard/my_courses?years={year}%2F{int(year) + 1}")
    soup = BeautifulSoup(r.text, features="html.parser")
    return soup.find_all("a")

def doIt(a_all, session, mode):
    threads = []
    heads = []
    falls = []
    springs = []
    summers = []
    for i in a_all:
        if "committee" in str(i):
            heads.append(i)
    #for i in range(1,4):
    i = mode
    for head in heads:
        
        if checkmode(head.contents[0], i):
            thread = threading.Thread(target=subjectInfo, args=(head, session, falls, springs, summers))
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    if i == 1:
        printGrades(falls, i)
    elif i == 2:
        printGrades(springs, i)
    else:   
        printGrades(summers, i)
        #printGrades(falls, springs, summers)
    st.session_state.grades = (falls, springs, summers)



def grades_page():
    st.title("ASU Grades Viewer - Grades")

    current_year = datetime.date.today().year
    sy = int("20"+str(st.session_state.Student_Year))
    gap = int(current_year) - sy
    # options list from 2020 to current year
    year_list = [str(i) for i in range(2020, current_year)]
    #year = st.text_input("Please Enter Academic Year (e.g., 2023 for 2023/2024):")
    year = st.selectbox("Please choose the year (e.g., 2023 for 2023/2024):",year_list)
    mode = st.selectbox("Please choose the semester", [("Fall", FALL_MODE), ("Spring", SPRING_MODE), ("Summer", SUMMER_MODE)], format_func=lambda x: x[0])[1]

    if st.button("Get Grades",type="primary"):
        session = st.session_state.session
        a_all = getYear(session, year)
        doIt(a_all, session, mode)


if st.session_state.session is None:
    login_page()
else:
    grades_page()
