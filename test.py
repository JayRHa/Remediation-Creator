from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient


client = GraphServiceClient(credentials=InteractiveBrowserCredential(), scopes=['https://graph.microsoft.com/.default'])

client.users