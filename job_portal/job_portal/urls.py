"""
URL configuration for job_portal project.

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
from django.http import HttpResponse
from django.urls import path, include
from django.contrib import admin

def health_check(request):
    return HttpResponse("✅ Django Job Portal is LIVE! 🚀")

urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),  # your existing URLs
]  # End of urlpatterns

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('accounts/', include('accounts.urls')),
#     path('jobs/', include('jobs.urls')),
#     path('', include('jobs.urls')),  # For homepage
#     path('admin-panel/', include('admin_panel.urls')),
    
# ]

# # Serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)