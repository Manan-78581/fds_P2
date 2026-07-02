from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Game, GameKey, Order, Publisher
from .permissions import IsPublisherOwnerOrReadOnly
from .serializers import (
    GameSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    PublisherSerializer,
)


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.select_related("user").all()
    serializer_class = PublisherSerializer
    permission_classes = [IsPublisherOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            return queryset
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.select_related("publisher", "publisher__user").all()
    serializer_class = GameSerializer
    permission_classes = [IsPublisherOwnerOrReadOnly]

    def perform_create(self, serializer):
        publisher = getattr(self.request.user, "publisher", None)
        if publisher is None:
            raise ValidationError("Only publisher accounts can create games.")
        serializer.save(publisher=publisher)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.select_related("user").prefetch_related("items", "items__game", "items__game_key")

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        order = write_serializer.save()
        read_serializer = OrderSerializer(order, context={"request": request})
        return Response(read_serializer.data, status=201)
