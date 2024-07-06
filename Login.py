import streamlit as st
import requests
from bs4 import BeautifulSoup


def login(mail, password):
    session = requests.session()
    url = 'https://eng.asu.edu.eg/login'
    login_data = {"email": mail, "password": password}
    x = session.get(url)
    soup = BeautifulSoup(x.text, features="html.parser")
    token = soup.find("input", {"name": "_token"})["value"]
    login_data["_token"] = token
    response = session.post(url, data=login_data)
    
    # Check for the presence of an error message in the HTML response
    soup = BeautifulSoup(response.text, features="html.parser")
    error_div = soup.find("div", class_="alert alert-danger")
    if error_div:
        return None, error_div.text.strip()
    return session, None


def login_page():
    st.title("ASU Grades Viewer")
    st.subheader("Login")
    with st.form(key='login_form'):
        id = st.text_input("Please enter your ID:")
        mail = id + "@eng.asu.edu.eg"
        password = st.text_input("Please enter your password: ", type="password")
        if st.form_submit_button(label='Login',type="primary"):
            session, error_message = login(mail, password)
            if error_message:
                st.error(error_message)
            else:
                st.session_state.session = session
                st.session_state.Student_Year = str(id[0:1])
                st.rerun()

