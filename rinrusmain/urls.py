"""rinrus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/',views.signup, name='signup'),
    path('log_in/',views.log_in, name='log_in'),
    path('log_out/',views.log_out, name='log_out'),
    path('build/', views.build, name='build'),
	path('search/',views.search, name='search'),
	path('results/',views.results, name='results'),
    path('forum/',views.forum, name='forum'),
	path('about/',views.about, name='about'),
	path('sim/<int:sim_ID>',views.sim_page, name='sim'),
    path('dl/<str:path>',views.download, name='dl')
	
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
