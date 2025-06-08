from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Пользовательское разрешение, позволяющее только владельцам объекта редактировать или удалять его.
    """
    def has_object_permission(self, request, view, obj):

        return obj.owner == request.user # Если владелец объекта совпадает с пользователем из запроса, то True. Иначе - False
    
    