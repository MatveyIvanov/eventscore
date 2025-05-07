from django.urls import include, path

v0 = [
    path("", include(("ping.urls", "ping"))),
]

urlpatterns = [
    path("api/v0/", include(v0)),
]
