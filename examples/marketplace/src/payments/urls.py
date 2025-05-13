from django.urls import include, path
from payments import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"payments", views.PaymentViewSet, basename="payments")

urlpatterns = [path("", include(router.urls))]
