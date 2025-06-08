from rest_framework import serializers
from .models import Car
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User (используется для отображения владельца автомобиля).
    Мы включаем только имя пользователя, так как не хотим раскрывать чувствительные данные.
    """
    class Meta:
        model = User
        fields = ['username'] # Отображаем только имя пользователя

class CarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Car.
    Преобразует объекты Car в JSON и обратно.
    """
    # Поле для отображения владельца автомобиля, используя UserSerializer
    owner = UserSerializer(read_only=True) # read_only=True означает, что это поле только для чтения,
                                          # и мы не будем его изменять при создании/обновлении Car через API.

    class Meta:
        model = Car
        # Поля, которые будут включены в API.
        fields = [
            'id', 'make', 'model', 'year', 'price', 'mileage', 'color',
            'description', 'is_available', 'created_at', 'updated_at', 'owner'
        ]
        # Поля, которые доступны только для чтения (не могут быть изменены через API POST/PUT/PATCH)
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        Переопределяем метод create, чтобы автоматически назначать
        текущего пользователя как 'owner' для нового автомобиля.
        """
        validated_data['owner'] = self.context['request'].user # Получаем текущего пользователя из контекста запроса
        return super().create(validated_data)