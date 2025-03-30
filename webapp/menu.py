import streamlit as st

def menu():
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Select an Option:", ["Home", "Generate Test Cases"])
    return option
