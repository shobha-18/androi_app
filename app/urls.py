from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    AndroidAppViewSet, 
    SignupView,  
    UserProfileView, 
    UserTaskView, 
    MyTokenObtainPairView, 
    logindata,app_list, 
    app_detail,LogoutView,User_detailsView,add_app
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# Create routers
router = DefaultRouter()
router.register(r'android-apps', AndroidAppViewSet, basename='android-app')

urlpatterns = [
    
    path('api/', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    
    path('signup/', views.SignupView, name='signup'),
    path('logindata/', views.logindata, name='logindata'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/tasks/', UserTaskView.as_view(), name='user-tasks'),
    path('user/', User_detailsView.as_view(), name='user-tasks'),

    

   
    path('', include(router.urls)),
    
    path('android/', views.app_list, name='android'),
    path("create",views.create,name="create"),
    path('android_c/', views.app_detail, name='app_detail'),
    
    path('add_app/', add_app.as_view(), name='add_app'),
    
    path('android-apps/<int:pk>/', app_detail, name='app_detail'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

