from django.shortcuts import render
from git_app.models import UserName
from git_app.forms import AddUserForm
import json
import requests
from threading import Thread
from django.views.generic import TemplateView
# Create your views here.


# page  which shows all the username from the database
def userpage(request):
    
    # form = AddUserForm()
    
    # # adding form handler+
    # if request.method == "POST": 
    #     form = AddUserForm(request.POST)

    #     if form.is_valid():
    #         form.save(commit=True)
    #         return userpage(request)
    #     else:
    #         print("ERROR ! FORM INVALID")

    user_list = UserName.objects.all()
    print(user_list)
    
    data_dict = {'user_list':user_list}
    # data_dict = {'user_list':user_list, 'form':form}

    return render(request, 'git_app/index.html', data_dict)


def userlistpage(request):
    user_list = UserName.objects.all()
    print(user_list)
    data_dict = {'user_list':user_list}
    return render(request, 'git_app/userlist.html', data_dict)

# page which shows all the repository of the user
def repopage(request, username=None):
    r = requests.get('https://api.github.com/users/'+username+'/repos')
    repos = []    
    if r.status_code == 404:
	    print("No such user")
    else:
        repos_json = json.loads(r.text)
        for i in repos_json:
            if i['fork'] == False:
    	        repos.append(i['name'])

    repo_dict = {'repo_list' : repos, 'username':username}
    return render(request, 'git_app/repos.html', repo_dict)
    

# for ploting the graph of commits on each repo
def graphpage(request, username=None, repo=None):
    commits=[]
    counts = []
    count=0
    # get commits for repo
    r = requests.get('https://api.github.com/repos/'+username+'/'+repo+'/commits')
    commits_json = json.loads(r.text)

    # if repo is committed even once
    if 'message' not in commits_json:
        for i in commits_json:
            datetime = i['commit']['committer']['date']
            date = datetime[:-1].split('T')[0]
            # get number of commits on each date for single repo
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

    print(counts, commits,end='\n\n')
    # sending commit-date along with number of commits on each date
    graph_dict = {'commits':json.dumps(commits), 'counts':json.dumps(counts)}
    return render(request, 'git_app/graph.html', graph_dict)
    


# doing same process as GRAPHPAGE but for all repository
def fullgraph(request, username=None):
    r = requests.get('https://api.github.com/users/'+username+'/repos')

    if r.status_code == 404:
        print("No such user")
    else:
        repos_json = json.loads(r.text)
        repos = []
        for i in repos_json:
            if i['fork'] == False:
                repos.append(i['name'])

        commit_data = []
        count_data = []
        for repo in repos:
            commits=[]
            counts = []

            r = requests.get('https://api.github.com/repos/'+username+'/'+repo+'/commits')
            commits_json = json.loads(r.text)
            count=0
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

            commit_data.append(commits)
            count_data.append(counts)
            
        print(repos, commit_data,end='\n\n')
        
        graph = {'username':username,'repo_data':json.dumps(repos), "commit_data":json.dumps(commit_data), "count_data":json.dumps(count_data)}
        return render(request, 'git_app/full_graph2.html', graph)


class new_repopage(TemplateView):
    commit_data = []
    count_data = []

    def commiter(self, repo):
        
        commits=[]
        counts = []

        r = requests.get('https://api.github.com/repos/'+self.username+'/'+repo+'/commits')
        commits_json = json.loads(r.text)
        count=0
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

        self.commit_data.append(commits)
        self.count_data.append(counts)

        print(commits, counts)

    # def new_repopage(request, username=None):
    def get(self, request, username=None):
        self.username = username
        r = requests.get('https://api.github.com/users/'+self.username+'/repos')

        if r.status_code == 404:   
            print("No such user")
            return render(request, 'git_app/error-404.html')
        else:
            repos_json = json.loads(r.text)
            repos = []
            
            for i, j in enumerate(repos_json):
                if i==0:
                    avatar_url = j['owner']['avatar_url']
                if j['fork'] == False:
                    repos.append(j['name'])

            repo_thead = []
            for repo in repos:
                repo_thead.append(Thread(target=self.commiter, args=(repo,)))
                repo_thead[-1].start()

            for thread in repo_thead:
                thread.join()
                
            graph = {'username':self.username,'avatar_url':avatar_url ,'repo_data': repos, "commit_data":json.dumps(self.commit_data), "count_data":json.dumps(self.count_data)}
            # print(graph)
            return render(request, 'git_app/new_repograph.html', graph)
            

