from django.urls import include, path

v0 = [
    path("", include("ping.urls", "ping")),
]

urlpatterns = [
    path("v0/", include(v0, "v0")),
]
