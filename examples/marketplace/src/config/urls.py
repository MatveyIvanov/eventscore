from django.urls import include, path

v0 = [
    path("", include(("products.urls", "products"))),
    path("", include(("payments.urls", "payments"))),
]

urlpatterns = [
    path("api/v0/", include(v0)),
]
