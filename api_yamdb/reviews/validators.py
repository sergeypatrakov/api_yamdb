from datetime import datetime

from django.core.exceptions import ValidationError


def validate_correct_year(year):
    """Проверяет, что год создания произведения <= текущему"""
    current_year = datetime.now().year
    if year > current_year:
        raise ValidationError(
            "Год написания произведения не может быть больше текущего",
            params={"value": year},
        )
