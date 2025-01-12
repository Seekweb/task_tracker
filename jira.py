# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from PyQt6.QtCore import QSettings
from requests.auth import HTTPBasicAuth
import json
import csv

class Jira:
    
    def __init__(self):
        self.settings= QSettings("Seekweb", "TaskTracker")
        self.url = self.settings.value("jiraUrl") #"https://jira.digitalpa.it/rest/api/2/search"
        jirauser = self.settings.value("jiraUser") #"a.tomassini"
        password = self.settings.value("jiraPass") #""
        self.auth = HTTPBasicAuth(jirauser, password)
      

    def getJiraID(self,id):
        if not self.url or not self.auth or not self.settings.value("jiraPass"):
            return 
        
        headers = {
            "Accept": "application/json"
        }
        
        jiraKey=f'WB-{id}'
        query = {
            'jql': f'project = WB AND assignee = {jirauser} AND id = {jiraKey} '
        }
        
        response = requests.request(
            "GET",
            self.url,
            headers=headers,
            params=query,
            auth=self.auth
        )
        print(response)
        data = json.loads(response.text)
        selectedIssues=[]
        #Get all issues and put them into an array
        for issue in data['issues']:
            return issue['fields']['summary']
        
    def getJiraCat(self,id):
        if not self.url or not self.auth or not self.settings.value("jiraPass"):
            return 
        
        
        headers = {
            "Accept": "application/json"
        }
        
        jiraKey=f'WB-{id}'
        query = {
            'jql': f'project = WB AND assignee = {jirauser}¨ AND id = {jiraKey} '
        }
        
        response = requests.request(
            "GET",
            self.url,
            headers=headers,
            params=query,
            auth=self.auth
        )
        print(response)
        data = json.loads(response.text)
        selectedIssues=[]
        #Get all issues and put them into an array
        for issue in data['issues']:
            return issue['fields']['project']['name']
    
    
    def saveJiraSetting(self,url,user,passw):
        self.settings.setValue("jiraUrl", url)
        self.settings.setValue("jiraUser", user)
        self.settings.setValue("jiraPass", passw)
        self.settings.sync()
