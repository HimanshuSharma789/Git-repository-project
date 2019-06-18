from django.urls import path
from git_app import views

app_name = 'git_app'

urlpatterns = [
    path('user/<str:username>', views.repopage),
]