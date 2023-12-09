import streamlit as st
import os
from msal_streamlit_authentication import msal_authentication
from modules.utility import Utility
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

#################################################################################
################################# Vars ##########################################
#################################################################################
st.set_page_config(page_title="GPT Remediation Creator", page_icon ="chart_with_upwards_trend", layout = 'wide')

if "login_token" not in st.session_state:
    st.session_state.login_token = InteractiveBrowserCredential().get_token("https://graph.microsoft.com/.default")
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
if "detection_script" not in st.session_state:
    st.session_state.detection_script = ""
if "remediation_script" not in st.session_state:
    st.session_state.remediation_script = ""

if "selections_scope" not in st.session_state:
    st.session_state.selections_scope = ["System", "User"] 
if "scope" not in st.session_state:
    st.session_state.scope = "System"

# Get graph token (Only needed if the website is deplyed)
# if debug
def get_graph_header(token):
    return {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}"
    }


# clinet_id = st.secrets["AZURE_CLIENT_ID"]
# tenant_id = st.secrets["AZURE_TENANT_ID"]
# redirect_uri = st.secrets["AZURE_REDIRECT_URI"]
# st.session_state.login_token = msal_authentication(
# auth={
#     "clientId": f"{clinet_id}",
#     "authority": f"https://login.microsoftonline.com/{tenant_id}",
#     "redirectUri": f"{redirect_uri}",
#     "postLogoutRedirectUri": "/"
# },
# cache={
#     "cacheLocation": "sessionStorage",
#     "storeAuthStateInCookie": False
# },
# logout_request={},
# login_button_text="Login",
# logout_button_text="Logout",
# html_id="html_id_for_button",
# key=1
# )
st.session_state.graph_auth_header = get_graph_header(st.session_state.login_token.token)
print(st.session_state.graph_auth_header)

utility = Utility(
    azure_openai_key=st.secrets["AZURE_OPENAI_KEY"]
    ,azure_openai_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
    ,azure_openai_deployment=st.secrets["AZURE_OPENAI_CHATGPT_DEPLOYMENT"]
    ,graph_auth_header=st.session_state.graph_auth_header
)
#################################################################################
################################# Page ##########################################
#################################################################################
st.title("GPT Remediation Creator")

st.markdown("This tool will help you create remediation steps for GPT violations. It will use the Azure OpenAI API to generate the remediation steps. You can then copy and paste the remediation steps into the GPT violation remediation section.")

def clear():
    st.session_state.description = ""
    st.session_state.scriptname = "WIN-NAMEOFYOURSCRIPT"
    st.session_state.generated = False
    st.session_state.detection_script = ""
    st.session_state.remediation_script = ""

tab1, tab2 = st.tabs(["Config", "Results"])
with tab1:
    #Get index of the selected item
    index = st.session_state.selections.index(st.session_state.selected)
    st.session_state.selected = st.selectbox(label="Select the scope:", options=st.session_state.selections, index=index)

    st.session_state.description = st.text_area(label="Enter your description / errorcode / etc. for the remediation here  (Very detailed description):", value=st.session_state.description)

    # Place the buttons beside each other
    col1, col2, col3 = st.columns([0.1, 0.1, 0.8])

    if col1.button("Generate"):
        try: 
            with st.spinner('Script will be generated...'):
                utility.generate()
                st.session_state.generated = True
            st.success('Script is generated. Change to the results tab!')
        except Exception as e:
            st.error(f"Error while generating the script: {e}")

    if col2.button("Clear"):
        clear()

with tab2:
    st.session_state.scriptname = st.text_input(label="Enter the name of the script here:", value=st.session_state.scriptname)

    index = st.session_state.selections_scope.index(st.session_state.scope)
    st.session_state.scope = st.selectbox(label="Select the scope:", options=st.session_state.selections_scope, index=index)

    col11, col21 = st.columns([0.5, 0.5])
    col11.title("Detection Script")
    col11.text_area(label="Detection Script:", value=st.session_state.detection_script)

    col21.title("Remediation Script")
    col21.text_area(label="Remediation Scripts:", value=st.session_state.remediation_script)

    if st.session_state.generated  == True:
        if st.button("Upload"):
            utility.upload(
                scope=st.session_state.scope
            )
            print("Upload")