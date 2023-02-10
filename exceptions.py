class CriticalException(Exception):
    """Критическае ошибка."""

    pass


class ApiException(Exception):
    """Нет запроса от API."""

    pass


class CheckResponseException(Exception):
    """Нет ключей от API."""

    pass


class StatusException(Exception):
    """Недокументированый статус."""

    pass
