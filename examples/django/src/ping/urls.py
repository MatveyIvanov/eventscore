from django.urls import include, path
from rest_framework.routers import SimpleRouter

from ping import views

router = SimpleRouter()
router.register(r"", views.PingViewSet, basename="ping")

urlpatterns = [
    path("", include(router.urls)),
]
