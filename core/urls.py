from django.urls import include, path

urlpatterns = [
    path("", include("core.modules.base.urls")),
    path("", include("core.modules.account.urls")),
    path("", include("core.modules.resident.urls")),
    path("", include("core.modules.fee.urls")),
]
