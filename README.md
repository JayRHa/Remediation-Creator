# Remediation Script Creator
- Find more informations in my blog post on [jannikreinhard.com](jannikreinhard.com)


![Alt text](https://github.com/JayRHa/Remediation-Creator/blob/main/.pictures/tool.png)

## Intro
Remediations play a pivotal role in effective client management, allowing organizations to proactively identify and resolve end-user issues. Additionally, they serve as a valuable tool for enforcing specific settings or configurations that may not be natively supported in Microsoft Intune. However, the process of crafting these scripts can often be intricate and time-consuming.

Imagine a solution where you can simply describe your desired configurations, and a tool generates the necessary scripts for you. If you find this idea appealing and are keen to explore such a solution, this blog is tailored to meet your exact needs.

## Contribution
<table>
  <tbody>
    <tr>
        <td align="center"><a href="https://github.com/JayRHa"><img src="https://avatars.githubusercontent.com/u/73911860?v=4" width="100px;" alt="Jannik Reinhard"/><br /><sub><b>Jannik Reinhard</b></sub></a><br /><a href="https://twitter.com/jannik_reinhard" title="Twitter">💬</a> <a href="https://www.linkedin.com/in/jannik-r/" title="LinkedIn">💬</a></td>
  </tbody>
</table>

## How does it work
In the end, the process is remarkably straightforward. The tool generates a detection script and, if desired, a remediation script based on your provided description. It then seamlessly uploads these scripts to your tenant, streamlining the entire process.


![Alt text](https://github.com/JayRHa/Remediation-Creator/blob/main/.pictures/howdoesitwork.png)

1. User authentication: The process starts with user authentication, ensuring that only authorized users can upload scripts using the user token
2. User describes the purpose of the script: After authentication, the user provides a description of what the script is intended to do.
3. Building a prompt with instructions and the description to generate a detection script: This description, along with instructions, is used to build a prompt for GPT-3.5-turbo, which will then generate a detection script based on the input.
4. (Optional) Building an additional prompt with instructions, the detection script, and the description to generate a remediation script: Optionally, a further step involves building another prompt that includes the instructions, the detection script that was generated, and the description. This new prompt is for GPT-3.5-turbo to create a remediation script, presumably to address the issues the detection script identified.
5. Display at web page: The scripts or the output from GPT-3.5-turbo are then displayed on a web page.
6. User presses upload and script will add to tenant: Finally, the user can press an upload button, resulting in the script being added to the tenant.


## Prerequisites
- GPT enabled Subscription (https://aka.ms/oai/access)

## Post steps
- Rename the secrets.toml.example to secrets.toml
- Once this is done fill out the informations in this file:
  - AZURE_OPENAI_KEY = "XXXXXXXXX"
  - AZURE_OPENAI_ENDPOINT = "https://YOURENDPOINTNAME.openai.azure.com"
  - AZURE_OPENAI_CHATGPT_DEPLOYMENT = "gpt-35-turbo"
  - APP_REGISTRATION_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e" # Default Graph App

## How to contribute?
If you have a ideas for improvements or for missing features as well as bugs, contact me via my blog, social media or open an issue on the repository with an description of your idea or make an pull request

## Disclosure
This is a community repository. There is no guarantee for this. Please check thoroughly before running the scripts.
