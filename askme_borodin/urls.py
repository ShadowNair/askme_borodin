"""
URL configuration for askme_borodin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('quastion/<int:quastion_id>', views.single_quastion, name='single_quastion'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
    path('ask', views.ask, name='ask'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name = 'logout'),
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
