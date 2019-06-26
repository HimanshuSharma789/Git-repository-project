from django.shortcuts import render
from git_app.models import UserName
from git_app.forms import AddUserForm
import json
import requests
from threading import Thread
from django.views.generic import TemplateView
# Create your views here.


# page  which shows all the username from the database

class userpage(TemplateView):
    def get(self, request):
        user_list = UserName.objects.all()
        print(user_list)
        
        data_dict = {'user_list':user_list}
        return render(request, 'git_app/index.html', data_dict)


class userlistpage(TemplateView):
    def get(self, request):
        user_list = UserName.objects.all()
        print(user_list)
        data_dict = {'user_list':user_list}
        return render(request, 'git_app/userlist.html', data_dict)
    

# doing same process as GRAPHPAGE but for all repository
class fullgraph(TemplateView):
    def get(self,request):
        return render(request, 'git_app/full_graph2.html')


class new_repopage(TemplateView):
    commit_data = []
    count_data = []
    headers = {'Authorization': 'token   <<<your key here>>>  '}

    def commiter(self, repo):
        
        commits=[]
        counts = []
    
        r = requests.get('https://api.github.com/repos/'+self.username+'/'+repo+'/commits', headers = self.headers)
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
        # print(commits, counts)

    def get(self, request, username=None):
        self.username = username
        r = requests.get('https://api.github.com/users/'+self.username+'/repos', headers = self.headers)

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
            print(graph)
            return render(request, 'git_app/new_repograph.html', graph)
            

