from django.test import TestCase
from requests import get, post
import json
# Create your tests here.


# Данные для входа
login_data = {
    "username": "admin",  # Замени на свой логин
    "password": "admin"  # Замени на свой пароль
}

# Отправляем запрос на получение токена
response = post(
    'http://127.0.0.1:8000/api/auth/token/',
    json=login_data
)

# Проверяем результат
if response.status_code == 200:
    data = response.json()
    token = data['token']
    print(f"✅ Токен получен: {token}")
    print(f"User ID: {data['user_id']}")
    print(f"Username: {data['username']}")
    
    # Сохраняем токен для дальнейших запросов
    with open('token.txt', 'w') as f:
        f.write(token)
else:
    print(f"❌ Ошибка: {response.status_code}")
    print(response.json())