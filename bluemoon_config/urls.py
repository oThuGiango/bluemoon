from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # # path('profile/', include('core.urls'))),
    # path('', include('home')),
    # path('accountmanage', include('accountmanage')),
    # path('demomanage', include('demomanage')),
    # path('test/', include('test')),
    # path('profile/', include('profile')),

    # path('hrmanage/', include('hrmanage')),
    # path('hredit/', include('hredit')),
]
