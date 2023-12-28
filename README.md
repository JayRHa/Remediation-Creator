# Remediation script creator
- Find more informations in my blog post on [jannikreinhard.com](jannikreinhard.com)

## Intro
As you know remediations are an essential part of the client management but also to become more proactive in detecting and solving issues of end users. It is also usefull to force settings or to set configurations which are not nativly supported in Intune. It is sometimes tricky and needs also some time to create the scripts. Wouldn't it be nice if you can only describe what you want have and a tool creates the scripts for you? If you are interested in such a solution than this blog address exacly your need!

## Contribution
<table>
  <tbody>
    <tr>
        <td align="center"><a href="https://github.com/JayRHa"><img src="https://avatars.githubusercontent.com/u/73911860?v=4" width="100px;" alt="Jannik Reinhard"/><br /><sub><b>Jannik Reinhard</b></sub></a><br /><a href="https://twitter.com/jannik_reinhard" title="Twitter">💬</a> <a href="https://www.linkedin.com/in/jannik-r/" title="LinkedIn">💬</a></td>
  </tbody>
</table>

## How does it work
In the end it is really simple the tool creates based on an description of you an detection and optional an remediation script and uploads this for you in your tenant.


![Alt text](https://github.com/JayRHa/Remediation-Creator/blob/main/.pictures/howdoesitwork.png)

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
