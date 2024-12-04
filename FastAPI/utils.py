from itsdangerous import URLSafeTimedSerializer


# JWT Token setup
SECRET_KEY = "URgbP75FiM!YkZPF535UZPucsUR*G8*@zt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

serializer = URLSafeTimedSerializer(
    secret_key=SECRET_KEY, salt="email-verification"
)

def create_url_safe_token(data: dict):

    token = serializer.dumps(data)

    return token