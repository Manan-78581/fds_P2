from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from games.viewsets import GameViewSet, OrderViewSet, PublisherViewSet
from games.views import HealthView, RegisterView

router = DefaultRouter()
router.register(r"publishers", PublisherViewSet, basename="publisher")
router.register(r"games", GameViewSet, basename="game")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", HealthView.as_view(), name="root"),
    path("admin/", admin.site.urls),
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/token/", obtain_auth_token, name="token"),
    path("api/", include(router.urls)),
]
