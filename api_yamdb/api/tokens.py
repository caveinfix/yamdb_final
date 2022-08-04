from rest_framework_simplejwt.tokens import AccessToken


def get_jwt_token(user):
    """Получает только jwt токен. В refresh токене нет необходимости."""
    token = AccessToken.for_user(user)
    token['email'] = user.email

    return {
        "token": str(token)
    }
