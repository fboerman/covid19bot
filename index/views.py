from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome, if you belong here you know where to go")