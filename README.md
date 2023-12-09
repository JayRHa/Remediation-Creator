# Remediation script creator
[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FJayRHa%2FGPTDeviceTroubleshooter%2Fmain%2Fazuredeploy.json)

- Find more informations in my blog post on jannikreinhard.com
## Intro


## Contribution
<table>
  <tbody>
    <tr>
        <td align="center"><a href="https://github.com/JayRHa"><img src="https://avatars.githubusercontent.com/u/73911860?v=4" width="100px;" alt="Jannik Reinhard"/><br /><sub><b>Jannik Reinhard</b></sub></a><br /><a href="https://twitter.com/jannik_reinhard" title="Twitter">💬</a> <a href="https://www.linkedin.com/in/jannik-r/" title="LinkedIn">💬</a></td>
  </tbody>
</table>

## How does it work
- Full infra deployment via ARM
- Code will be pulled from GitHub
- User delegated permissions to authenticate on graph
- Azure App Service for the website and the code logic

![Alt text](https://github.com/JayRHa/GPTDeviceTroubleshooter/blob/main/.pictures/auth.png)

![Alt text](https://github.com/JayRHa/GPTDeviceTroubleshooter/blob/main/.pictures/flow.png)

## Prerequisites
- GPT enabled Subscription (https://aka.ms/oai/access)
- App registration with deligated permissions (DeviceManagementConfiguration.Read.All, DeviceManagementManagedDevices.Read.All, DeviceManagementApps.Read.All, Group.Read.All, User.Read, Device.Read.All)

![Alt text](https://github.com/JayRHa/GPTDeviceTroubleshooter/blob/main/.pictures/appRegistartion.png)

## Deployment
[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FJayRHa%2FGPTDeviceTroubleshooter%2Fmain%2Fazuredeploy.json)

## Post steps
- Fill out in the App Service Settings the variables (APPLICATION_ID, AZURE_OPENAI_KEY)

## How to contribute?
If you have a ideas for improvements or for missing features as well as bugs, contact me via my blog, social media or open an issue on the repository with an description of your idea.

## Disclosure
This is a community repository. There is no guarantee for this. Please check thoroughly before running the scripts.
