from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPublisherOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "user", None)
        if owner is None and hasattr(obj, "publisher"):
            owner = obj.publisher.user
        return owner == request.user
