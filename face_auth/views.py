from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from .forms import RegistrationForm,LoginForm
from .models import User
from django.urls import reverse

from django.http.response import StreamingHttpResponse
from .camera import gen_frames
from django.contrib.auth import authenticate,login,logout
# from django.contrib.auth.forms import AuthenticationForm

# Create your views here.

def logout_user(request):
    """
    If the user is authenticated, set the user's face_auth field to False, log the user out, and
    redirect to the home page
    
    :param request: The request object
    :return: A redirect to the homepage.
    """
    if request.user.is_authenticated:
        user = User.objects.get(uid=request.user.uid)
        user.face_auth = False
        user.save()
        logout(request)
    return redirect('/')


def home(request):
    """
    It takes a request object as an argument, and returns a response object
    
    :param request: The request is an HttpRequest object
    :return: The render function is being called.
    """
    return render(request,'index.html')

# It creates a view for the registration form.
# The get_context_data method is used to add the next parameter to the context, and the
# get_success_url method is used to redirect to the next URL if it exists
class RegistrationView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm

    def get_context_data(self, *args, **kwargs):
        context = super(RegistrationView, self).get_context_data(*args, **kwargs)
        context['next'] = self.request.GET.get('next')
        return context

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        success_url = reverse('login')
        if next_url:
            success_url += '?next={}'.format(next_url)

        return success_url

# def gen(camera):
# 	while True:
# 		frame = camera.get_frame()
# 		yield (b'--frame\r\n'
# 				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
# def two_factor(request,user):
#     return render(request,'feed.html')

def welcome(request,user):
    """
    If the user has face authentication enabled, disable it, log them in, and render the welcome page.
    
    :param request: The request object is a Python object that encapsulates all of the HTTP request data
    sent by the client
    :param user: The username of the user who is logging in
    :return: The user is being returned.
    """
    user = User.objects.get(username = user)
    if user.face_auth:
        user.face_auth = False
        user.save()
        login(request,user)
    return render(request,'welcome.html')

def facecam_feed(request,user):
    """
    It takes a request and a user, and returns a StreamingHttpResponse object that contains a stream of
    frames from the user's webcam
    
    :param request: The request object
    :param user: The user whose facecam feed is being requested
    :return: A StreamingHttpResponse object.
    """
    user = User.objects.get(username=user)
    stream = gen_frames(request,user)
    return StreamingHttpResponse(stream,content_type='multipart/x-mixed-replace; boundary=frame')

def login_user(request):
    """
    If the request method is POST, then validate the form, if the form is valid, then authenticate the
    user, if the user is authenticated, then render the feed.html page, else render the login page with
    an error message
    
    :param request: The request object is a standard Django object that contains metadata about the
    request sent to the server
    :return: the rendered template.
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                # login(request,user)
                return render(request,'feed.html',{'user':user.username})
            else:
                return render(request,'registration/login.html',{'form':form,'error':'Invalid Credentials'})
        else:
            return render(request,'registration/login.html',{'form':form})

    form = LoginForm()
    return render(request,'registration/login.html',{'form':form})

def checkAuth(request,user):
    """
    It takes a request and a user, and returns a JSON object with the value of the user's face_auth
    field
    
    :param request: The request object
    :param user: the username of the user
    :return: A JsonResponse object.
    """
    val = User.objects.get(username=user)
    return JsonResponse({'auth':val.face_auth})
