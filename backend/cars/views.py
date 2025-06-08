from rest_framework import viewsets, permissions
from .models import Car
from .serializers import CarSerializer
from .permissions import IsOwner # Импортируем наш новый класс разрешений
from .filters import CarFilter

class CarViewSet(viewsets.ModelViewSet):
    """
    API-представление для модели Car.
    Предоставляет CRUD-операции (создание, чтение, обновление, удаление) для автомобилей.
    """
    queryset = Car.objects.all().order_by('-created_at') # Получаем все автомобили, отсортированные по дате создания
    serializer_class = CarSerializer # Используем наш CarSerializer для преобразования данных
    filterset_class = CarFilter # Класс фильтров
    search_fields = ['make', 'model', 'description'] # Поля для SearchFilter
    ordering_fields = ['price', 'year', 'created_at'] # Поля для OrderingFilter

    def get_permissions(self):
        """
        Настройка прав доступа в зависимости от действия.
        """
        if self.action == 'create':
            # Для создания автомобиля - пользователь должен быть аутентифицирован (IsAuthenticated)
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Для обновления или удаления - пользователь должен быть владельцем автомобиля или иметь права администратора
            self.permission_classes = [permissions.IsAdminUser | IsOwner]
        else:
            # Для чтения (list, retrieve) - любой может просматривать
            self.permission_classes = [permissions.AllowAny]
        return [permission() for permission in self.permission_classes]