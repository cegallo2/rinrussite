from django.http import HttpResponse,HttpResponseRedirect, Http404, HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import Simulation
from django.urls import reverse
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files import File
from django.core.exceptions import ValidationError
import datetime, logging, os
from .scripts import processing_script as ps
from . import models

def home(request):
    return render(request,'rinrusmain/home.html')

def log_out(request):
    logout(request)
    return render(request,'rinrusmain/home.html')

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        if confirm != password:
            return render(request,'rinrusmain/signup.html',
            {'signup_error':'Passwords did not match each other'})

        if not (User.objects.filter(username=username).exists()
        or User.objects.filter(email=email).exists()):

            user = User.objects.create_user(username,
                                            email,
                                            password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            print(username, "SIGNED UP")

            return render(request,'rinrusmain/login.html')

        else:
            return render(request,'rinrusmain/signup.html',
            {'signup_error':'Username/Password does not match records'})

    return render(request,'rinrusmain/signup.html')

def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user, "IS LOGGED IN")

        if user is not None:
            login(request,user)
            return render(request,'rinrusmain/home.html')
        else:
            return render(request,'rinrusmain/log_in.html',
            {'login_error':'Username/Password does not match records'})

    return render(request,'rinrusmain/log_in.html')   

def build(request):
    if not request.user.is_authenticated:
        return render(request,'rinrusmain/home.html')
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        folder='rinrusmain/static/files/'+request.POST["jobName"] + '/'
        fs = FileSystemStorage(location=folder) 
        print(myfile.content_type)
        try:
            if (myfile.content_type == 'application/octet-stream'
             or myfile.content_type =='application/xml-external-parsed-entity'): 
                if len(models.Simulation.objects.filter(simName=request.POST["jobName"]))>0:
                    return render(request, 'rinrusmain/build.html',{'uploaded_file_error': "Duplicate Job Name"})  
                chainTemp=request.POST["row1"]+request.POST["row2"]+request.POST["row3"]+request.POST["row4"]+request.POST["row5"]
                chainTemp=[str(i) for i in chainTemp]
                chainTemp=filter(lambda a:a != '*',chainTemp)
                chainTemp=[str(i) for i in chainTemp]
                residueTemp=request.POST["text1"]+"|"+request.POST["text2"]+"|"+request.POST["text3"]+"|"+request.POST["text4"]+"|"+request.POST["text5"]+"|"
                residueTemp=residueTemp.split('|')
                residueTemp=list(filter(None,residueTemp))
                print(request.POST["jobName"])
                fileName=request.POST["jobName"]+".pdb"
                filename = fs.save(fileName, myfile)
                uploaded_file_url = '/'+request.POST["jobName"] + '/'+fs.url(filename) #run processing is selected
                case='no_sim'
                if request.POST['run_processing']=="yes":
                    try:
                        sim_result=ps.run_scripts(uploaded_file_url, residueTemp, chainTemp, request.POST["jobName"])
                        if sim_result=='good':
                            case="sim_success"
                        else:
                            case="sim_fail"
                    except Exception as e: 
                        logging.exception("message") #eventually print logs to a file
                        print("Simulation Failed")     
                        case='sim_fail'
                else: 
                    print("bad beans")   
                temp_obj=Simulation(unProcessedPDBURL=uploaded_file_url,residue=residueTemp,chain=chainTemp,simName=request.POST["jobName"], userName=request.POST["userName"], modelVersion=1.2) #remember to change model version when making changes
                temp_obj.save()
                if case=='no_sim':
                    return render(request, 'rinrusmain/build.html', {'uploaded_file_url': uploaded_file_url, 'uploaded_file_error':'No Simulation'})
                elif case=='sim_fail':
                    return render(request, 'rinrusmain/build.html', {'uploaded_file_url': uploaded_file_url, 'uploaded_file_error':'Simulation Failed, Check Log', 'sim_page':temp_obj})
                else:
                    return render(request, 'rinrusmain/build.html', {'uploaded_file_url': uploaded_file_url, 'uploaded_file_error':'Simulation Successful', 'sim_page':temp_obj})
                    
            else:   
                      return render(request, 'rinrusmain/build.html',{'uploaded_file_error': "Improper file type"})
        except Exception as e:
            print(e)
            return render(request, 'rinrusmain/build.html',{'uploaded_file_error': "Model failed to create"})
    return render(request,'rinrusmain/build.html')

def search(request):
    if not request.user.is_authenticated:
        return render(request,'rinrusmain/home.html')
    return render(request,'rinrusmain/search.html')

    
def results(request):
    if not request.user.is_authenticated:
        return render(request,'rinrusmain/home.html')
    if request.method == 'GET':
        text=request.GET.get('textField', None)
        type=request.GET.get('searchType', None)
        date=request.GET.get('dateIn',None)
        date
        simulations=[]
        if(type=="Show All"):
            simulations = list(models.Simulation.objects.all().order_by('-idNumber'))
        elif(type=="Job Name"):
            simulations = list(models.Simulation.objects.filter(simName__icontains=text))
        elif(type=="ID Number"):
            simulations = list(models.Simulation.objects.filter(idNumber=int(text)))
        elif(type=="Organization"):
            simulations = list(models.Simulation.objects.filter(userName__icontains=text))
        elif(type=="Date"):
            simulations = list(models.Simulation.objects.filter(dateRan__date=date))
        
        #print(simulations)
        return render(request,'rinrusmain/results.html',{'simulations' : simulations})
        
def sim_page(request,sim_ID):
    if not request.user.is_authenticated:
        return render(request,'rinrusmain/home.html')

    print("dog")
    model=Simulation.objects.filter(idNumber=sim_ID).first()
    
    unProcFile  = open(settings.MEDIA_ROOT+ model.unProcessedPDBURL, "r") 
    unProcFile = File(unProcFile)

    
    print("DOG HERE")
    return render(request,'rinrusmain/sim_page.html',{'simulation' : model}) 
    
def forum(request):
    if not request.user.is_authenticated:
        return render(request,'rinrusmain/home.html')

    return render(request,'rinrusmain/forum.html')
        
def about(request):
    return render(request,'rinrusmain/about.html')



def download(request, path):
    print(settings.MEDIA_ROOT)
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
