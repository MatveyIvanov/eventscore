from django.urls import include, path
from ping import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"", views.PingViewSet, basename="ping")

urlpatterns = [
    path("", include(router.urls)),
]
