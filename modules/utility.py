""""""
import streamlit as st
import openai

detection_script_system_prompt = """
[MUST] Create a PowerShell script for Microsoft Intune that detects a specific issue on Windows devices.
[MUST] The script should only detect the issue without changing, fixing, or remediating it.
[MUST] Utilize the provided sample or template script as a basis, modifying it according to your specific detection needs.
[MUST] Ensure the script returns an Exit Code 0 if the issue is not detected, and Exit Code 1 if the issue is detected.
[MUST] The output must be in JSON format, following this example: {"ExitCode": 0, "Message": "No issue detected"}.
"""


remdaition_system_prompt = """
[MUST] Develop a PowerShell remediation script for Microsoft Intune, specifically for Windows devices.
[MUST] This script should perform actions to remediate the detected issue, based on the detection script's findings.
[MUST] Customize the script to target the specific remediation actions required for your scenario.
[MUST] Ensure the script returns appropriate Exit Codes based on the success or failure of the remediation process.
[MUST] Provide clear output in JSON format, indicating the status of the remediation, e.g., {"ExitCode": 0, "Message": "Issue remediated successfully"}.
[MUST] The script must be adaptable based on user inputs or script parameters to handle different remediation scenarios.
[MUST] Include comprehensive error handling and documentation within the script for ease of understanding and maintenance.
 """

def __generate_remediations__(question:str):
    prompt = f"""
    You have to develope two sctipts. One remediation and one detection script. You have to follwo the following rules:

    #Detection Script
    {detection_script_system_prompt}

    #Remediation Script
    {remdaition_system_prompt}

    # This is te purpose of the script:
    {question}

    # Output
    The output MUST be an valid JSON object with the following structure:

    """ + '{"detectionScript" : "VALID POWERSHELL CODE", "remediationScript" : "VALID POWERSHELL CODE"}'



    pass
def __generate_detection__():
    pass

def clear():
    st.session_state.description = ""
    st.session_state.scriptname = "WIN-NAMEOFYOURSCRIPT"
    st.session_state.generated = False

def generate():
    if st.session_state.description == "":
        st.error("Please enter a description")
        return
    if st.session_state.scriptname == "" or st.session_state.scriptname == "WIN-NAMEOFYOURSCRIPT":
        st.error("Please enter a scriptname or change the default value")
        return
    
    if st.session_state.selected == "Detection only":
        __generate_detection__()
    else:
        __generate_remediations__()