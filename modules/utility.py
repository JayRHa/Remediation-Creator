""" """
import streamlit as st
import json
import requests
import base64

DETECTION_SCRIPT_PROMPT = """
When forming a response, the following rules must be adhered to:

Rules:

1. You must create a PowerShell script specifically for Microsoft Intune that  is capable of detecting a particular issue on Windows devices.
2. Ensure that the script addresses edge cases, conducts necessary validations, and adheres to PowerShell best practices.
3. Include relevant comments within the code to elucidate the logic and aid other developers in comprehending the implementation.
4. The script must only perform detection of the issue, without implementing any changes, repairs, or remediation.
5. Use the provided sample or template script as a foundation, modifying it to suit your specific detection requirements.
6. Make sure the script returns an Exit Code 0 if the issue is not detected, and an Exit Code 1 if the issue is detected.
7. The script should only detect issues without making any changes to the system.
8. The output should follow this example format:

```PowerShell
Write-Host "No issue detected"
exit 0 # or exit 1
```

Additional Information:

- The script will always be executed with administrative privileges.
"""


REMEDIATION_SCRIPT_PROMPT = """
When creating a response, you must adhere to the following rules:

Rules:

1. Develop a PowerShell remediation script specifically for Microsoft Intune, designed for Windows devices.
2. Ensure the script handles edge cases, conducts necessary validations, and upholds PowerShell best practices.
3. Include detailed comments within the code to clarify the logic and help other developers grasp the implementation.
4. The script should enact measures to rectify the detected issue, building upon the findings of the detection script.
5. Tailor the script to cater to the specific remediation actions required for your scenario.
6. Ensure the script provides appropriate Exit Codes reflecting the remediation process's success or failure.
7. The script must be flexible, permitting adaptation.
8. Incorporate thorough error handling and documentation within the script for easy understanding and maintenance.
9. The output should follow this example format:

```PowerShell
Write-Host "No issue detected"
exit 0 # or exit 1
```

Additional Information:

- The script will always be executed with administrative privileges.
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