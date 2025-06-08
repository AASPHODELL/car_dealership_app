from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Car
from .serializers import CarSerializer # Импортируем наш CarSerializer

class CarViewSet(viewsets.ModelViewSet):
    """
    API-представление для модели Car.
    Предоставляет CRUD-операции (создание, чтение, обновление, удаление) для автомобилей.
    """
    queryset = Car.objects.all().order_by('-created_at') # Получаем все автомобили, отсортированные по дате создания
    serializer_class = CarSerializer # Используем наш CarSerializer для преобразования данных
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Права доступа

    # Дополнительно: Разрешаем только владельцу редактировать/удалять свой автомобиль
    def get_permissions(self):
        """
        Настройка прав доступа в зависимости от действия.
        """
        if self.action in ['create']:
            # Для создания автомобиля - пользователь должен быть аутентифицирован
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Для обновления или удаления - пользователь должен быть владельцем или администратором
            # (Пока не реализовано "владелец", но IsAuthenticatedOrReadOnly уже ограничивает)
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            # Для чтения (list, retrieve) - любой может просматривать
            self.permission_classes = [permissions.AllowAny]
        return [permission() for permission in self.permission_classes]