from django.shortcuts import render
from git_app.models import UserName
from git_app.forms import AddUserForm
import json
import requests
from threading import Thread
from django.views.generic import TemplateView
# Create your views here.


# handle request for the main page
    # when the request is GET
        # takes all the username fron the database model
        # pass the data in form of dict to html page
        # render index.html and pass the dict to it
class userpage(TemplateView):
    def get(self, request):
        user_list = UserName.objects.all()
        data_dict = {'user_list':user_list}
        return render(request, 'git_app/index.html', data_dict)


# handle dashboard page requests
class new_repopage(TemplateView):
    commit_data = []
    count_data = []
    repo_data = []

    # pass the auth key to perform multiple search from the github-api
    # write your own auth key for successful request to the server 
    headers = {'Authorization': 'token <<your_token_here>> '}


    # each thread extracts detail about commit for each repo
    def commiter(self, repo):

        # clearing previous data
        self.commit_data = []
        self.count_data = []
        self.repo_data = []

        commits=[]
        counts = []
    
        # request for commit information for the repo
        r = requests.get('https://api.github.com/repos/'+self.username+'/'+repo+'/commits', headers = self.headers)
        commits_json = json.loads(r.text)
        count=0

        # check if no commit is done on a repo
        # if exists the create 2 list  ---- 1. commit dates  ----   2. commit count on those date 
        # simple if else rule to count number of commits for each repo
        if 'message' not in commits_json:
            for i in commits_json:
                datetime = i['commit']['committer']['date']
                date = datetime[:-1].split('T')[0]
                if not commits:
                    commits.append(date)
                    count+=1
                elif commits[-1] == date:
                    count+=1
                else:
                    commits.append(date)
                    counts.append(count)
                    count=1
            counts.append(count)

        # saving the commit data for each repo
        # adding all the data for each repo to form a 2 - list of commit-date and commit-counts
        self.repo_data.append(repo)
        self.commit_data.append(commits)
        self.count_data.append(counts)


    # when the get request occurs 
    def get(self, request, username=None):
        self.username = username
        # make request to the api for the repo of following username ; provided with auth-key as header
        r = requests.get('https://api.github.com/users/'+self.username+'/repos', headers = self.headers)

        # if user does not exist (status code is 404)
        if r.status_code == 404:
            # render error page from template directory   
            return render(request, 'git_app/error-404.html')
        else:
            # convert the text to python-json format for easy retrieval
            repos_json = json.loads(r.text)
            repos = []
            
            # extracting all the repository-name owned by the user
            for i, j in enumerate(repos_json):
                if i==0:
                    avatar_url = j['owner']['avatar_url']           # user profile pic
                if j['fork'] == False:                              # repo is forked or not
                    repos.append(j['name'])

            # initiating the thread for multiple request to the server
            repo_thead = []
            for repo in repos:
                # commiter function is invoked and a repo is passed as an argument
                repo_thead.append(Thread(target=self.commiter, args=(repo,)))
                repo_thead[-1].start()

            # joining all the threads
            for thread in repo_thead:
                thread.join()
                
            # send all the data collected as in form of dictionary to the webpage
            graph = {'username':self.username,'avatar_url':avatar_url ,'repo_data': self.repo_data, "commit_data":json.dumps(self.commit_data), "count_data":json.dumps(self.count_data)}
            print(graph)
            return render(request, 'git_app/new_repograph.html', graph)
            


# provide more options for the repo checking
class fullgraph(TemplateView):
    def get(self,request):
        # renders full_graph page
        return render(request, 'git_app/full_graph2.html')