import re

from rest_framework import serializers


def validate_username(value: str) -> str:
    """
    Validate the username to ensure it contains
    only valid characters and is not 'me'.

    Args:
        value (str): The username string to be validated.

    Returns:
        str: The validated username if no invalid characters are found.

    Raises:
        serializers.ValidationError:
        If the username contains invalid characters or is 'me'.
    """

    invalid_chars_regex = re.compile(r'[^\w.@+-]+')
    invalid_chars = re.findall(invalid_chars_regex, value)
    if invalid_chars:
        raise serializers.ValidationError(
            'Имя пользователя содержит недопустимые'
            f'символы: {", ".join(invalid_chars)}',
        )
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Имя пользователя не может быть "me".',
        )
    return value
