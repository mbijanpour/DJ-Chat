"""
URL configuration for DJchat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from server.views import ServerListViewSet

# the router is used for generating urls for our API endpoints "ServerListViewSet"
# this will generate all the urls dedicated to the CRUD operations (GET, POST, PUT, DELETE)
router = DefaultRouter()
router.register("api/server/select", ServerListViewSet, basename="server")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/ui/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
] + router.urls

# this code snippet will create the url media files which can be later accessible by this url with
# the help of static() function (note: this is only done in development phase)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
