from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet # Импортируем наш ViewSet

# Создаем роутер для автоматической генерации URL-адресов для ViewSet
router = DefaultRouter()
router.register(r'cars', CarViewSet) # Регистрируем CarViewSet под префиксом 'cars'

urlpatterns = [
    path('', include(router.urls)), # Включаем URL-адреса, сгенерированные роутером
]