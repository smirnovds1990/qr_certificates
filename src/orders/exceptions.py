from rest_framework.exceptions import APIException


class CertificateNotFoundError(APIException):
    status_code = 404
    default_detail = "Сертификат не найден."
    default_code = "certificate_not_found"


class CertificateDesignNotFoundError(APIException):
    status_code = 404
    default_detail = "Изображение не найдено."
    default_code = "certificate_design_not_found"


class CertificateOrderNotFoundError(APIException):
    status_code = 404
    default_detail = "Заказ не найден."
    default_code = "order_not_found"


class UnexpectedYokassaNotificationStatusError(APIException):
    status_code = 400
    default_detail = "Неизвестный статус платежа от ЮКассы."
    default_code = "unexpected_yookassa_notification_status"


class SendEmailError(APIException):
    status_code = 500
    default_detail = "Ошибка при отправке письма клиенту."
    default_code = "send_email_error"


class CertificateOrderCreateError(APIException):
    status_code = 500
    default_detail = "Ошибка при создании клиента и заказа."
    default_code = "process_certificate_order_error"


class NoConfirmationReturnedError(APIException):
    status_code = 502
    default_detail = "Ошибка при создании платежа."
    default_code = "yookass_confirmation_error"


class CertificateOrderStatusValidationError(APIException):
    status_code = 400
    default_detail = "Неизвестный статус заказа."
    default_code = "certificate_order_status_error"
