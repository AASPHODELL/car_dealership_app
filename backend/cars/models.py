from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    """
    Модель, представляющая автомобиль для продажи.
    """
    make = models.CharField(max_length=100, verbose_name="Марка") # Например, Toyota, BMW
    model = models.CharField(max_length=100, verbose_name="Модель") # Например, Camry, X5
    year = models.IntegerField(verbose_name="Год выпуска") # Год производства
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена") # Цена автомобиля, до 10 цифр, 2 после запятой
    mileage = models.IntegerField(verbose_name="Пробег", null=True, blank=True) # Пробег, опционально
    color = models.CharField(max_length=50, verbose_name="Цвет", null=True, blank=True) # Цвет, опционально
    description = models.TextField(verbose_name="Описание", null=True, blank=True) # Подробное описание, опционально
    is_available = models.BooleanField(default=True, verbose_name="В наличии") # Доступен ли сейчас для продажи
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления") # Автоматически заполняется при создании
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления") # Автоматически обновляется при изменении

    # Связь с пользователем, который добавил автомобиль (например, менеджер)
    owner = models.ForeignKey(User, related_name='cars', on_delete=models.CASCADE, verbose_name="Добавил(а)")

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ['-created_at'] # Сортировка по дате добавления (новые сверху)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
