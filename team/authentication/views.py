from base64 import urlsafe_b64decode, urlsafe_b64encode
from distutils.log import error
from email.message import EmailMessage
from lib2to3.pgen2 import token
from lib2to3.pgen2.tokenize import generate_tokens
import pkgutil
from django.utils.encoding import force_bytes,force_text
from cgitb import html

import email
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import authentication,login,user,logout
from django.contrib import messages
from team import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from . tokens import generate_token



# Create your views here.
def home(request):
    return render(request,"authentication/index.html")

def signup(request):

    if request.method == "POST":
        # username=request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if user.objects.filter(username=username):
            messages.error(request,"username already exist!please try other username")

            if user.objects.filter(email=email):
                messages.error(request,"Email alreadyregistered ")
                return redirect("home")

            if len(username)>10:
                messages.error(request,"username must be uder 10 characters")

            if pass1 != pass2:
                messages.error(request,"passwords didn't match!")


            if not username.isalnum(): 
                messages.error(request,"username must be Alpha-Numeric!")
                return redirect("home")   



    myuser= User.objects.create_user(username,email,pass1)
    myuser.first_name =fname
    myuser.last_name =lname 
    myuser.is_active = False
    myuser.save() 

    messages.success(request,'your account has been successful created. we have send you a confirmationa email, please confirm your email in order to activate your account.')

    # welcome email

    subject="Welcome to Solace - Django login!!"
    message= "Hello!" + myuser.first_name + "!! \n" + "Welcometo Solace!! \n Thank you visiting our website \n We have also send you a confirmation email,please confirm your email address in order to activate your account \n\n Thanking you \n Jane Musimbi"
    from_email = settings.EMAIL_HOST_USER
    to_list =[myuser.email]
    send_email(subject,message,from_email,to_list,fail_silently=True)


    # Email Address Confirmation Email

    current_site = get_current_site=(request) 
    email_subject= "confirm you email @ solace_Django Login!!"
    message2= render_to_string("email_confirmation.html"),{
        'name':myuser.first_name,
        'domain':current_site.domain,
        'uid':urlsafe_b64encode(force_bytes(myuser.pk)), 
        'token':generate_tokens.make_token(myuser),
    }
    email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER
        [myuser.email],
    )
    email.fail_silently= True
    send_mail()

    return redirect ('signin')
    

    return render(request,"authentication/signup.html")

def signin(request):
    if request.method == "POST":
        username =request.POST['username']
        pass1 =request.POST["pass1"]

        User = authentication(username=username,password=pass1)
        if User is not None:
            login(request,User)
            fname=user.first_name

            return render(request,"authentication/index.html",{'fname':fname})  

        else:
            messages.error(request,"bad credetials!")
            return redirect("home")

    return render(request,"authentication/signin.html")  

def signup(request):
    logout(request)
    messages.success(request, "Logged out Succefully")
    return redirect('home')

def activate(request,uidb64,token):
    try:
        uid= force_text(urlsafe_b64decode(uidb64))
        myuser= user.objects.get(pk-uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

        if myuser is not None and generate_token.check_token(myuser,token):
            myuser.is_active=True
            myuser.save()
            login(request,myuser)
            return redirect('home')
        else:
            return render(request,"activation_failed.html")    
       

