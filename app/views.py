from django.shortcuts import render,redirect
from django.contrib import messages
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions,status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser, AndroidApp, UserTask
from .serializers import UserSerializer, AndroidAppSerializer, UserTaskSerializer,MyTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import JsonResponse
from django.views import View
from rest_framework.decorators import action,api_view
from django.shortcuts import get_object_or_404



class AndroidAppViewSet(viewsets.ViewSet):
    def get_permissions(self):
       if self.action in ['list','retrieve''create','update','delete']:  
        return [AllowAny()]
       return [IsAuthenticated()]  
            

    def list(self, request):
        apps = AndroidApp.objects.all()
        serializer = AndroidAppSerializer(apps, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        app = get_object_or_404(AndroidApp, pk=pk)
        points = request.data.get('points')
        if points is not None:
            try:
                app.points += int(points) 
                app.save()
                return Response({"status": "Points updated", "points": app.points})
            except ValueError:
                return Response({"error": "Invalid points value"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Points not provided"}, status=status.HTTP_400_BAD_REQUEST)


def app_list(request):
    return render(request, 'app_list.html')

def app_detail(request, pk):
    
    app = get_object_or_404(AndroidApp, pk=pk)

    
    return render(request, 'index.html', {'app': app})
def create(request):
    if request.method == 'POST':
        try:
            # Parse JSON data if sent as JSON
            data = JSONParser().parse(request) if request.content_type == 'application/json' else request.POST
            
            serializer = AndroidAppSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
class User_detailsView(View):
    def get(self, request):
        apps = AndroidApp.objects.all()
        return render(request, 'user_profile.html', {'apps': apps})
class add_app(View):
    def get(self, request):
        
        return render(request, 'add_app.html')


@csrf_exempt
def SignupView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        retype_password = request.POST.get('password')
        is_admin = request.POST.get('is_admin') == 'on'  

        user = CustomUser.objects.create_user(username=username, password=password)
        if is_admin:
            user.is_admin = True  
            user.is_staff = True  
            user.save()

        return redirect('logindata')
    return render(request, 'signup.html')



class token_view(APIView):
    def post(self, request):
        user = CustomUser.objects.get(username=request.data['username'])
        if user.check_password(request.data['password']):
            refresh = RefreshToken.for_user(user)
            return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
        return Response({"detail": "Invalid credentials"}, status=400)

@csrf_exempt
def logindata(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  
            print(f"Username: {user.username}, is_admin: {getattr(user, 'is_admin', None)}")

            if getattr(user, 'is_admin', False):  
                return redirect('android')  
            else:
                return redirect('user-tasks')  
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


class UserProfileView(APIView):
    def get(self, request):
        
        user = CustomUser.objects.first()  
        if not user:
            return Response({"error": "No user found"}, status=404)
        
        serializer = UserSerializer(user)  
        return Response(serializer.data)

class UserTaskView(APIView):
    def get(self, request):
        """Handles GET requests to retrieve all tasks for the current user."""
        try:
            
            custom_user = CustomUser.objects.get(username=request.user.username)
            
            
            tasks = UserTask.objects.filter(user=custom_user)
            serializer = UserTaskSerializer(tasks, many=True)
            
            return Response(serializer.data, status=200)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request):
        
        try:
            
            custom_user = CustomUser.objects.get(username=request.user.username)
            
            
            app_name = request.data.get('app_name')
            if not app_name:
                return Response({'error': 'App name is required'}, status=400)
            
            android_app = AndroidApp.objects.get(name=app_name)
            
            
            task = UserTask.objects.create(
                user=custom_user,
                app=android_app,
                screenshot=request.data['screenshot'],
            )
            
            return Response(UserTaskSerializer(task).data, status=201)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except AndroidApp.DoesNotExist:
            return Response({'error': f'AndroidApp with name "{app_name}" not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out."})

    def get(self, request):  
        logout(request)
        return Response({"detail": "Successfully logged out."})


