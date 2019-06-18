from django.shortcuts import render
from git_app.models import UserName
import json
import requests
# Create your views here.

def userpage(request):
    user_list = UserName.objects.all()
    user_dict = {'user_list':user_list}
    print(user_dict)
    return render(request, 'git_app/users.html', user_dict)

def repopage(request, username=None):
    r = requests.get('https://api.github.com/users/'+username+'/repos')
    repos = []    
    if r.status_code == 404:
	    print("No such user")
    else:
        repos_json = json.loads(r.text)
        for i in repos_json:
    	    repos.append(i['name'])

    repo_dict = {'repo_list' : repos}

    return render(request, 'git_app/repos.html', repo_dict)