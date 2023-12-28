""" """
import streamlit as st
import json
import requests
import base64

DETECTION_SCRIPT_PROMPT = """
[MUST] Create a PowerShell script for Microsoft Intune that detects a specific issue on Windows devices.
[MUST] The script should only detect the issue without changing, fixing, or remediating it.
[MUST] Utilize the provided sample or template script as a basis, modifying it according to your specific detection needs.
[MUST] Ensure the script returns an Exit Code 0 if the issue is not detected, and Exit Code 1 if the issue is detected.
[MUST] Never change something on the system only detect!
[MUST] The output must be like following this example: 
Write-Host "No issue detected"
exit 0 # or exit 1
"""


REMEDIATION_SCRIPT_PROMPT = """
[MUST] Develop a PowerShell remediation script for Microsoft Intune, specifically for Windows devices.
[MUST] This script should perform actions to remediate the detected issue, based on the detection script's findings.
[MUST] Customize the script to target the specific remediation actions required for your scenario.
[MUST] Ensure the script returns appropriate Exit Codes based on the success or failure of the remediation process.
[MUST] The script must be adaptable based on user inputs or script parameters to handle different remediation scenarios.
[MUST] Include comprehensive error handling and documentation within the script for ease of understanding and maintenance.
[MUST] The output must be like following this example: 
Write-Host "Issue remediated successfully"
exit 0 # or exit 1
 """

BASE_URL = "https://graph.microsoft.com/beta/"

class Utility:
    def __init__(self, azure_openai_key:str, azure_openai_endpoint:str, azure_openai_deployment:str, graph_auth_header:str):
        """ Init Utility calls """
        self.azure_openai_key = azure_openai_key
        self.azure_openai_endpoint = azure_openai_endpoint
        self.azure_openai_deployment = azure_openai_deployment
        self.graph_auth_header = graph_auth_header
    
    def invoke_gpt_call(self,user:str,system:str=None,history:str=None):
        """ Invoke the Azure OpenAI API"""
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
        

    def run_graph(self, endpoint:str, body:dict):
        """ Run a graph call"""
        uri = BASE_URL + endpoint
        print(body)
        try:
            response = requests.post(uri, headers=self.graph_auth_header, json=body)
        except Exception as e:
            raise(f"Error while executing a call to {uri}: {e}")
        response.raise_for_status()
            
    def __generate_remediations__(self,description:str, detection_script:str):
        prompt = f"""
Create a endpoint analytics remediation script which fits to the detection script based on the following description:
{description}

# Detection script
{detection_script}

The output MUST only be an valid Powershell script without description or text
"""

        st.session_state.remediation_script = self.invoke_gpt_call(
            user=prompt
            ,system=REMEDIATION_SCRIPT_PROMPT
            ,history=None
        )
        return st.session_state.remediation_script

    def __generate_detection__(self, description:str):
        prompt = f"""
Create a endpoint analytics detection script based on the following description:
{description}

The output MUST only be an valid Powershell script without description or text
"""

        st.session_state.detection_script = self.invoke_gpt_call(
            user=prompt
            ,system=DETECTION_SCRIPT_PROMPT
            ,history=None
        )
        return st.session_state.detection_script

    def upload(self, scope:str="System") -> None:
        if st.session_state.scriptname == "" or st.session_state.scriptname == "WIN-NAMEOFYOURSCRIPT":
            st.error("Please enter a scriptname or change the default value")
            return False
            
        if st.session_state.detection_script == "":
            st.error("Please generate the detection script")
            return  False
        else:
            # Encode and then decode to convert bytes to string
            base64_det_script = base64.b64encode(st.session_state.detection_script.encode("utf-8")).decode('utf-8')

        base64_rem_script = ""
        if st.session_state.remediation_script != "":
            # Encode and then decode to convert bytes to string
            base64_rem_script = base64.b64encode(st.session_state.remediation_script.encode("utf-8")).decode('utf-8')

        body = {
            "displayName": st.session_state.scriptname,
            "description": st.session_state.description,
            "publisher": "GPT Remediation Creator",
            "runAs32Bit": True,
            "runAsAccount": scope,  # Ensure 'scope' is defined earlier in your code
            "enforceSignatureCheck": False,
            "detectionScriptContent": base64_det_script,
            "remediationScriptContent": base64_rem_script,
            "roleScopeTagIds": ["0"]
        }

        # Convert to json
        #body = json.dumps(body)

        endpoint = "deviceManagement/deviceHealthScripts"
        self.run_graph(endpoint=endpoint, body=body)
        return True


    def generate(self) -> None:
        """ Generate the scripts"""
        if st.session_state.description == "":
            st.error("Please enter a description")
            return
        self.__generate_detection__(description = st.session_state.description)
        if st.session_state.selected == "Detection and Remediation":
            self.__generate_remediations__(description = st.session_state.description, detection_script = st.session_state.detection_script)