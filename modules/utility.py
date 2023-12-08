""""""
import streamlit as st
import openai
import requests


DETECTION_SCRIPT_PROMPT = """
[MUST] Create a PowerShell script for Microsoft Intune that detects a specific issue on Windows devices.
[MUST] The script should only detect the issue without changing, fixing, or remediating it.
[MUST] Utilize the provided sample or template script as a basis, modifying it according to your specific detection needs.
[MUST] Ensure the script returns an Exit Code 0 if the issue is not detected, and Exit Code 1 if the issue is detected.
[MUST] The output must be in JSON format, following this example: {"ExitCode": 0, "Message": "No issue detected"}.
"""


REMEDIATION_SCRIPT_PROMPT = """
[MUST] Develop a PowerShell remediation script for Microsoft Intune, specifically for Windows devices.
[MUST] This script should perform actions to remediate the detected issue, based on the detection script's findings.
[MUST] Customize the script to target the specific remediation actions required for your scenario.
[MUST] Ensure the script returns appropriate Exit Codes based on the success or failure of the remediation process.
[MUST] Provide clear output in JSON format, indicating the status of the remediation, e.g., {"ExitCode": 0, "Message": "Issue remediated successfully"}.
[MUST] The script must be adaptable based on user inputs or script parameters to handle different remediation scenarios.
[MUST] Include comprehensive error handling and documentation within the script for ease of understanding and maintenance.
 """


class Utility:
    def __init__(self, azure_openai_key, azure_openai_endpoint, azure_openai_deployment, graph_auth_header):
        self.azure_openai_key = azure_openai_key
        self.azure_openai_endpoint = azure_openai_endpoint
        self.azure_openai_deployment = azure_openai_deployment
        self.graph_auth_header = graph_auth_header
    
    def invoke_gpt_call(self,user,system=None,history=None):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.azure_openai_key
        }

        messages = []

        if system is not None:
            messages.append({
                "role": "system",
                "content": system
            })

        if history is not None:
             messages = messages + history

        messages.append({
            "role": "user",
            "content": user
        })

        body = {
            "messages": messages,
            "temperature": 0
        }

        try:
            response = requests.post(f"{self.azure_openai_endpoint}/openai/deployments/{self.azure_openai_deployment}/chat/completions?api-version=2023-05-15", headers=headers, data=json.dumps(body))
            response.raise_for_status()
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error while executing a call to {self.azure_openai_endpoint}: {e}")
            return None
            
    def __generate_remediations__(self,question:str):
        prompt = f"""
        You have to develope two sctipts. One remediation and one detection script. You have to follwo the following rules:

        #Detection Script
        {DETECTION_SCRIPT_PROMPT}

        #Remediation Script
        {REMEDIATION_SCRIPT_PROMPT}

        # This is te purpose of the script:
        {question}

        # Output
        The output MUST be an valid JSON object with the following structure:

        """ + '{"detectionScript" : "VALID POWERSHELL CODE", "remediationScript" : "VALID POWERSHELL CODE"}'


        pass
    def __generate_detection__(self):
        pass

    def clear():
        st.session_state.description = ""
        st.session_state.scriptname = "WIN-NAMEOFYOURSCRIPT"
        st.session_state.generated = False

    def generate(self):
        if st.session_state.description == "":
            st.error("Please enter a description")
            return
        if st.session_state.scriptname == "" or st.session_state.scriptname == "WIN-NAMEOFYOURSCRIPT":
            st.error("Please enter a scriptname or change the default value")
            return
        
        if st.session_state.selected == "Detection only":
            self.__generate_detection__()
        else:
            self.__generate_remediations__()