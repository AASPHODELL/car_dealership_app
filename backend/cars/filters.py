import django_filters
from .models import Car

class CarFilter(django_filters.FilterSet):
    """
    Класс фильтров для модели Car.
    Позволяет фильтровать автомобили по марке, модели, году и статусу наличия.
    """
    # Фильтрация по диапазону цен (price_min, price_max)
    price = django_filters.RangeFilter()
    # Фильтрация по году выпуска (year_min, year_max)
    year = django_filters.RangeFilter()
    # Поиск по марке, модели и описанию (использует 'icontains' для нечувствительного к регистру поиска)
    search = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label='Search by description'
    )
    # Пример для фильтрации по марке, модели (точное совпадение)
    make = django_filters.CharFilter(lookup_expr='iexact')
    model = django_filters.CharFilter(lookup_expr='iexact')
    color = django_filters.CharFilter(lookup_expr='iexact')


    class Meta:
        model = Car
        # Поля, по которым разрешена точная фильтрация
        fields = ['make', 'model', 'year', 'is_available', 'color', 'price', 'search']