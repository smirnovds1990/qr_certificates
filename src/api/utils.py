from rest_framework.request import Request


def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Если запрос идет через прокси, то
        # X-Forwarded-For будет содержать список IP, разделенных запятой.
        # IP клиента будет первый в списке
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        # Если прокси не используется, то IP находится в REMOTE_ADDR.
        ip = request.META.get("REMOTE_ADDR")
    return ip
