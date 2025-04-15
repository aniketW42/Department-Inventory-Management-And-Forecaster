from django.contrib import admin
from django.urls import path, include   
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),    
    path('notifications/', include('notifications.urls')),
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='user/change_password.html',
        success_url='/change-password-done/'
    ), name='change_password'),

    path('change-password-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='user/change_password_done.html'
    ), name='change_password_done'),

]
