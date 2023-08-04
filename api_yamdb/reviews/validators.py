import re

from django.conf import settings
from rest_framework.exceptions import ValidationError


def username_validator(value):
    regex = r"^[\w.@+-]+\Z"
    if re.search(regex, value) is None:
        invalid_characters = set(re.findall(r"[^\w.@+-]", value))
        raise ValidationError(
            (
                f"Не допустимые символы {invalid_characters} в username. "
                f"username может содержать только буквы, цифры и "
                f"знаки @/./+/-/_."
            ),
        )

    if value.lower() == settings.USER_READ_EDIT_URL:
        raise ValidationError(
            f"Использовать имя   '{settings.USER_READ_EDIT_URL}' в качестве "
            f"username запрещено."
        )
