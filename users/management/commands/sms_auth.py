import os
import random

import requests
from dotenv import load_dotenv

load_dotenv()

verification_codes = {}


def send_verification_code(phone_number):
    code = random.randint(100000, 999999)
    message_text = f"Ваш код подтверждения: {code}"

    data = {
        "api_id": os.getenv("API_SMS_TOKEN"),
        "to": phone_number,
        "msg": message_text,
        "json": 1,
        "test": 0,
    }

    try:
        response = requests.post("https://sms.ru/sms/send", data=data)
        response_data = response.json()

        if response.status_code == 200:
            if response_data.get("status") == "OK":
                sms_status = response_data.get("sms", {}).get(phone_number, {})
                if sms_status.get("status") == "OK":
                    print(f"✓ SMS успешно отправлено на {phone_number}")
                    print(f"Код подтверждения: {code}")
                    verification_codes[phone_number] = str(code)
                    return code
                else:
                    print(f"Ошибка отправки SMS: {sms_status.get('status_text')}")
            else:
                print(f"Ошибка API: {response_data.get('status_text')}")
        else:
            print(f"HTTP ошибка: {response.status_code}")

    except Exception as e:
        print(f"Ошибка при отправке запроса: {str(e)}")

    return None


def main():
    phone = input("Введите номер телефона (в формате +7xxxxxxxxxx): ")
    generated_code = send_verification_code(phone)
    if not generated_code:
        print("Не удалось отправить SMS. Проверить баланс или настройки.")
        return

    attempts = 3
    for _ in range(attempts):
        user_input_code = input("Введите полученный код: ")
        if user_input_code == str(generated_code):
            print("Код подтвержден успешно!")
            return
        else:
            print("Неверный код, попробуйте снова.")

    print("Предел попыток исчерпан. Попробуйте позже.")


if __name__ == "__main__":
    main()
