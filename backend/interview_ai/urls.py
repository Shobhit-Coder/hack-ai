from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Accept both without and with trailing slash at the include boundary
    path('api/dashboard', include('dashboard.urls')),     # no-slash alias
    path('api/jobs', include('jobs.urls')),               # no-slash alias
    path('api/candidates', include('candidates.urls')),   # no-slash alias
    path('api/interviews', include('interviews.urls')),   # no-slash alias
    path('api/dashboard/', include('dashboard.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/candidates/', include('candidates.urls')),
    path('api/interviews/', include('interviews.urls')),
]
