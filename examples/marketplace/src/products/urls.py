from django.urls import include, path
from products import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"products", views.ProductViewSet, basename="products")

urlpatterns = [path("", include(router.urls))]
