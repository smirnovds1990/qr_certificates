# qr_certificates

Приложение для оформления и оплаты электронного QR-код сертификата.
___
1. Установите Docker согласно [инструкции](https://docs.docker.com/desktop/).
2. Установите переменные окружения согласно `.env.example`.
Пояснения к некоторым переменным:
- **YOOKASSA_ACCOUNT_ID** — ID вашего магазина
- **RETURN_URL** — URL для редиректа при оплате через ЮКассу
- **YOOKASSA_NOTIFICATION_IPS** — IP, с которых может прийти уведомление от ЮКассы. 
    Указаны в [документации](https://yookassa.ru/developers/using-api/webhooks):
    - 185.71.76.0/27
    - 185.71.77.0/27
    - 77.75.153.0/25
    - 77.75.156.11
    - 77.75.156.35
    - 77.75.154.128/25
    - 2a02:5180::/32
- **BASE_URL** — базовый URL приложения вида: https://<domain.ru>/admin/orders/certificateorder/

- Настройки SMTP сервера для отправки сертификатов пользователям:
    - **EMAIL_HOST**
    - **EMAIL_PORT**
    - **EMAIL_HOST_USER**
    - **EMAIL_HOST_PASSWORD**
Инструкция по настройке Яндекс SMTP-сервера — https://yandex.ru/support/yandex-360/business/mail/ru/mail-clients/others#smtpsetting
3. Установите в личном кабинете ЮКассы URL для уведомлений об изменении статусов платежей.
Личный кабинет --> Интеграция --> HTTP-уведомления --> Изменить настройки
URL должен быть вида — `https://<domain.ru>/api/v1/changed-payment-status/`
4. Запуск:
```bash
cd qr_certificates
docker compose up -d --build
```