"""
URL configuration for IMDBClone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/imdb/home', permanent=False)),
    path('admin/', admin.site.urls),
    path('admin/view-site/', RedirectView.as_view(url=reverse_lazy('home'))),
    path('imdb/', include('django.contrib.auth.urls')),
    path("imdb/", include("IMDB.urls")),
    path('imdb/login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
