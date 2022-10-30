"""enterprisehubs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from apps.account import views as error

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include('apps.bookings.urls')),
    url(r'^backend/', include('apps.members.urls')),
    url(r'^backend/', include('apps.staff.urls')),
    url(r'^backend/', include('apps.billables.urls')),
    url(r'^backend/', include('apps.blog.urls')),
    url(r'^backend/', include('apps.membersite.urls')),
    url(r'^backend/', include('apps.account.urls')),
    url(r'^backend/', include('apps.services.urls')),
    url(r'^backend/', include('apps.facility.urls')),
    url(r'^backend/', include('apps.programs.urls')),
    url(r'^', include('apps.onboarding.urls')),
    url(r'^', include('django.contrib.auth.urls')),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler403 = error.error_403
handler404 = error.error_404
handler500 = error.error_500

