from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from cars.models import Car

class CarAPITestCase(APITestCase):
    """
    Набор тестов для API-эндпоинтов модели Car.
    Использует APITestCase для тестирования API.
    """
    def setUp(self):
        # Метод setUp выполняется перед каждым тестом
        # Создаем тестовых пользователей и автомобили
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin_password')
        self.owner_user = User.objects.create_user('owner', 'owner@example.com', 'owner_password')
        self.other_user = User.objects.create_user('other', 'other@example.com', 'other_password')

        # Создаем API-клиентов для разных пользователей
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        self.owner_client = APIClient()
        self.owner_client.force_authenticate(user=self.owner_user)

        self.other_client = APIClient()
        self.other_client.force_authenticate(user=self.other_user)

        self.anon_client = APIClient() # Клиент для неаутентифицированных пользователей

        # Создаем тестовые автомобили
        self.car1 = Car.objects.create(
            make='Toyota', model='Camry', year=2020, price=1500000.00,
            mileage=50000, color='Black', description='Reliable sedan',
            is_available=True, owner=self.owner_user
        )
        self.car2 = Car.objects.create(
            make='Honda', model='CRV', year=2018, price=1800000.00,
            mileage=70000, color='White', description='Family SUV',
            is_available=False, owner=self.other_user
        )
        self.car3 = Car.objects.create(
            make='BMW', model='X5', year=2022, price=4500000.00,
            mileage=20000, color='Blue', description='Luxury SUV',
            is_available=True, owner=self.owner_user
        )

        # URL-адреса для API
        self.list_url = reverse('car-list') # car-list это имя, которое генерирует DefaultRouter для списка
        self.detail_url = lambda pk: reverse('car-detail', kwargs={'pk': pk}) # car-detail для деталей

    def test_get_car_list_public(self):
        """
        Проверка получения списка автомобилей неаутентифицированным пользователем.
        """
        response = self.anon_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_get_car_detail_public(self):
        """
        Проверка получения деталей конкретного автомобиля неаутентифицированным пользователем.
        """
        response = self.anon_client.get(self.detail_url(self.car1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['make'], 'Toyota')
        self.assertEqual(response.data['id'], self.car1.pk)

    # --- Тесты POST-запросов (Создание) ---

    def test_create_car_authenticated(self):
        """
        Проверка создания автомобиля аутентифицированным пользователем.
        """
        data = {
            'make': 'Audi',
            'model': 'A4',
            'year': 2023,
            'price': 3000000.00,
            'mileage': 10000,
            'color': 'Grey',
            'description': 'Sporty sedan',
            'is_available': True
        }

        response = self.owner_client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Car.objects.count(), 4) # Убедимся, что автомобиль добавлен
        self.assertEqual(response.data['make'], 'Audi')
        self.assertEqual(response.data['owner']['username'], self.owner_user.username) # Проверяем, что owner установлен

    def test_create_car_unauthenticated(self):
        """
        Проверка попытки создания автомобиля неаутентифицированным пользователем.
        Должен быть отказ (401 Unauthorized).
        """
        data = {
            'make': 'Tesla', 'model': 'Model 3', 'year': 2024,
            'price': 5000000.00, 'is_available': True
        }

        response = self.anon_client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Car.objects.count(), 3) # Убедимся, что автомобиль не добавлен

    # --- Тесты PUT/PATCH-запросов (Обновление) ---

    def test_update_car_owner(self):
        """
        Проверка обновления автомобиля его владельцем.
        """
        updated_data = {
            'make': 'Subaru',
            'model': 'Forester',
            'year': 2021,
            'price': self.car1.price, 
            'mileage': self.car1.mileage,
            'color': self.car1.color,
            'description': self.car1.description,
            'is_available': self.car1.is_available,
        }

        response = self.owner_client.put(self.detail_url(self.car1.pk), updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car1.refresh_from_db() # Обновляем объект из базы данных
        self.assertEqual(self.car1.make, 'Subaru')
        self.assertEqual(self.car1.model, 'Forester')
        self.assertEqual(self.car1.year, 2021) # Проверяем измененный год

    def test_update_car_other_user_forbidden(self):
        """
        Проверка попытки обновления автомобиля другим аутентифицированным пользователем.
        Должен быть отказ (403 Forbidden) из-за IsOwnerOrReadOnly.
        """
        updated_data = {'make': 'New Make', 'model': 'New Model'}
        response = self.other_client.put(self.detail_url(self.car1.pk), updated_data, format='json') # car1 принадлежит owner_user
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.car1.refresh_from_db()
        self.assertNotEqual(self.car1.make, 'New Make') # Убеждаемся, что не изменилось

    def test_update_car_unauthenticated_forbidden(self):
        """
        Проверка попытки обновления автомобиля неаутентифицированным пользователем.
        Должен быть отказ (401 Unauthorized).
        """
        updated_data = {'make': 'Ghost Car'}
        response = self.anon_client.put(self.detail_url(self.car1.pk), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.car1.refresh_from_db()
        self.assertNotEqual(self.car1.make, 'Ghost Car')

    # --- Тесты DELETE-запросов (Удаление) ---

    def test_delete_car_owner(self):
        """
        Проверка удаления автомобиля его владельцем.
        """
        response = self.owner_client.delete(self.detail_url(self.car1.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) # No Content при успешном удалении
        self.assertEqual(Car.objects.count(), 2) # Убедимся, что автомобиль удален (было 3 машины в списке, а стало 2)
        self.assertFalse(Car.objects.filter(pk=self.car1.pk).exists())

    def test_delete_car_other_user_forbidden(self):
        """
        Проверка попытки удаления автомобиля другим аутентифицированным пользователем.
        Должен быть отказ (403 Forbidden).
        """
        response = self.other_client.delete(self.detail_url(self.car1.pk)) # car1 принадлежит owner_user
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Car.objects.count(), 3) # Убедимся, что автомобиль не удален

    def test_delete_car_unauthenticated_forbidden(self):
        """
        Проверка попытки удаления автомобиля неаутентифицированным пользователем.
        Должен быть отказ (401 Unauthorized).
        """
        response = self.anon_client.delete(self.detail_url(self.car1.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Car.objects.count(), 3) # Убедимся, что автомобиль не удален

    # --- Тесты Фильтрации ---

    def test_filter_by_make(self):
        """
        Проверка фильтрации по марке автомобиля.
        """
        response = self.anon_client.get(self.list_url + '?make=Toyota')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['make'], 'Toyota')

    def test_filter_by_is_available(self):
        """
        Проверка фильтрации по статусу наличия.
        """
        response = self.anon_client.get(self.list_url + '?is_available=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # car1 и car3 доступны
        self.assertEqual(len(response.data['results']), 2)
        # Убедимся, что car2 (is_available=False) не попал
        self.assertFalse(any(car['make'] == 'Honda' for car in response.data['results']))

    def test_filter_by_year_range(self):
        """
        Проверка фильтрации по диапазону годов.
        """
        response = self.anon_client.get(self.list_url + '?year_min=2019&year_max=2021')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1) # Только Toyota Camry (2020)
        self.assertEqual(response.data['results'][0]['make'], 'Toyota')

    # --- Тесты Поиска ---

    def test_search_description(self):
        """
        Проверка текстового поиска по описанию (и другим полям).
        """
        response = self.anon_client.get(self.list_url + '?search=Reliable')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['make'], 'Toyota')

    def test_search_no_results(self):
        """
        Проверка поиска, когда нет совпадений.
        """
        response = self.anon_client.get(self.list_url + '?search=NonExistentPhrase')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    # --- Тесты Сортировки ---
    
    def test_ordering_by_price(self):
        """
        Проверка сортировки по цене (по возрастанию).
        """
        response = self.anon_client.get(self.list_url + '?ordering=price')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что результаты отсортированы по цене
        prices = [car['price'] for car in response.data['results']]
        # Преобразуем цены в числа для сравнения
        prices = [float(p) for p in prices]
        self.assertEqual(prices, sorted(prices))

    def test_ordering_by_year_desc(self):
        """
        Проверка сортировки по году (по убыванию).
        """
        response = self.anon_client.get(self.list_url + '?ordering=-year')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что результаты отсортированы по году по убыванию
        years = [car['year'] for car in response.data['results']]
        self.assertEqual(years, sorted(years, reverse=True))
