#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Adlean API
Отправляет несколько запросов подряд (реклама показывается после N-го запроса)
"""
import urllib.request
import urllib.error
import time
import json

# Настройки API (взяты из конфига проекта)
ADLEAN_API_KEY = "ad-pQZBmuIVpUm1aIAXlxDjQzsaWh5pIVC6PYzc2rRPgkcnRG1Q5Pu5S6sw0c7Qv"
ADLEAN_API_URL = "https://api.adlean.pro/engine/send_message"
TEST_USER_ID = "test_user_67890"

# Список тестовых запросов
TEST_MESSAGES = [
    "Как выложить песню на Spotify?",
    "Как настроить рекламу в социальных сетях?",
    "Какие программы лучше для записи музыки?",
    "Как продвигать музыку в интернете?",
]


def send_request(message: str, request_number: int):
    """Отправка одного запроса к API"""
    
    print(f"\n{'='*70}")
    print(f"ЗАПРОС #{request_number}")
    print(f"{'='*70}")
    print(f"📝 Текст: {message}")
    
    # Формируем payload
    payload = {
        "text": message,
        "role": "user",
        "timestamp": int(time.time()),
        "chat_id": f"chat_{TEST_USER_ID}",
        "user_type": "non_authorized",
        "user_metadata": {
            "country": "RU",
            "gender": "unknown",
            "ip": "0.0.0.0"
        }
    }
    
    try:
        # Кодируем payload в JSON
        data = json.dumps(payload).encode('utf-8')
        
        # Создаём запрос с заголовками
        request = urllib.request.Request(
            ADLEAN_API_URL,
            data=data,
            headers={
                "accept": "application/json",
                "Auth": ADLEAN_API_KEY,
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        # Отправляем запрос
        start_time = time.time()
        with urllib.request.urlopen(request, timeout=10) as response:
            elapsed = time.time() - start_time
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
        
        if status_code == 200:
            data = json.loads(response_data)
            have_ads = data.get("have_ads", False)
            content = data.get("content", "") or ""
            show_price = data.get("show_price", 0.0)
            click_price = data.get("click_price", 0.0)
            
            print(f"✅ Status: {status_code} | Time: {elapsed:.2f}с")
            print(f"📊 have_ads: {have_ads}")
            print(f"💰 show_price: {show_price} | click_price: {click_price}")
            
            if have_ads and content:
                print(f"\n{'🎯 РЕКЛАМА ПОЛУЧЕНА! 🎯':^70}")
                print(f"{'='*70}")
                print(content)
                print(f"{'='*70}")
                return True
            else:
                print(f"ℹ️  Реклама не показана")
                return False
        else:
            print(f"❌ Ошибка: Status {status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Основная функция - отправка нескольких запросов"""
    
    print("\n" + "="*70)
    print("ТЕСТИРОВАНИЕ ADLEAN API - МНОЖЕСТВЕННЫЕ ЗАПРОСЫ")
    print("="*70)
    print(f"🌐 API URL: {ADLEAN_API_URL}")
    print(f"👤 User ID: {TEST_USER_ID}")
    print(f"📝 Количество запросов: {len(TEST_MESSAGES)}")
    print("="*70)
    
    ads_received = False
    
    for i, message in enumerate(TEST_MESSAGES, 1):
        if send_request(message, i):
            ads_received = True
            break  # Прерываем после первой полученной рекламы
        
        # Небольшая пауза между запросами
        if i < len(TEST_MESSAGES):
            time.sleep(0.5)
    
    print(f"\n{'='*70}")
    print("ИТОГО")
    print(f"{'='*70}")
    if ads_received:
        print("✅ Реклама была успешно получена!")
    else:
        print("ℹ️  Реклама не была показана ни для одного из запросов")
        print("   Это может быть нормальным поведением API:")
        print("   - Нет доступных рекламных кампаний")
        print("   - Реклама показывается не на каждый запрос")
        print("   - Нужно больше запросов от пользователя")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

