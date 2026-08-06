import streamlit as st

st.title("Resume Manager")
st.subheader("Login page")

username = st.text_input("Username")

password = st.text_input(
    "Password",
    type="password",
)

if st.button("Login"):
    st.write("Login button clicked")