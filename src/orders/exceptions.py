from rest_framework.exceptions import APIException


class CertificateNotFoundError(APIException):
    status_code = 404
    default_detail = "Сертификат не найден."
    default_code = "certificate_not_found"


class CertificateOrderNotFoundError(APIException):
    status_code = 404
    default_detail = "Заказ не найден."
    default_code = "order_not_found"


class UnexpectedYokassaNotificationStatus(APIException):
    status_code = 400
    default_detail = "Неизвестный статус платежа от ЮКассы."
    default_code = "unexpected_yookassa_notification_status"


class SendEmailError(APIException):
    status_code = 500
    default_detail = "Ошибка при отправке письма клиенту."
    default_code = "send_email_error"


class CertificateOrderCreateException(APIException):
    status_code = 500
    default_detail = "Ошибка при создании клиента и заказа."
    default_code = "process_certificate_order_error"
