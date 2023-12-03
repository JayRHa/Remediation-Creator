import streamlit as st
import os
from modules.utility import *
from msal_streamlit_authentication import msal_authentication

#################################################################################
################################# Vars ##########################################
#################################################################################
st.set_page_config(page_title="GPT Remediation Creator", page_icon ="chart_with_upwards_trend", layout = 'wide')


if "login_token" not in st.session_state:
    st.session_state.login_token = {}
if "graph_auth_header" not in st.session_state:
    st.session_state.graph_auth_header = {}
if "question" not in st.session_state:
    st.session_state.question = ""
if "selections" not in st.session_state:
    st.session_state.selections = ["Detection only", "Detection and Remediation"]
if "selected" not in st.session_state:
    st.session_state.selected = "Detection and Remediation"

if "description" not in st.session_state:
    st.session_state.description = ""
if "scriptname" not in st.session_state:
    st.session_state.scriptname = "WIN-NAMEOFYOURSCRIPT"
if "generated" not in st.session_state:
    st.session_state.generated = False

#################################################################################
################################# Page ##########################################
#################################################################################
st.title("GPT Remediation Creator")

st.markdown("This tool will help you create remediation steps for GPT violations. It will use the Azure OpenAI API to generate the remediation steps. You can then copy and paste the remediation steps into the GPT violation remediation section.")

tab1, tab2 = st.tabs(["Config", "Results"])
with tab1:
    #Get index of the selected item
    index = st.session_state.selections.index(st.session_state.selected)
    st.session_state.selected = st.selectbox(label="Select the scope", options=st.session_state.selections, index=index)

    st.session_state.description = st.text_area(label="Enter your description / errorcode / etc. for the remediation here", value=st.session_state.description)
    st.session_state.scriptname = st.text_input(label="Enter the name of the script here", value=st.session_state.scriptname)

    # Place the buttons beside each other
    col1, col2, col3 = st.columns([0.1, 0.1, 0.8])

    if col1.button("Generate"):
        generate()
        st.session_state.generated = True

    if col2.button("Clear"):
        clear()

with tab2:
    col11, col21 = st.columns([0.5, 0.5])
    col11.title("Detection Script")
    col11.text_area(label="Detection Script:")

    col21.title("Remediation Script")
    col21.text_area(label="Remediation Script:")

    if st.session_state.generated  == True:
        if st.button("Upload"):
            print("Upload")



print(st.secrets["AZURE_OPENAI_KEY"])

login_token = None