# config/auth/cookie_jwt_authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from loguru import logger
from django.conf import settings


class BaseCookieJWTAuthentication(JWTAuthentication):
    """
    Base class for cookie JWT authentication with Loguru logging.
    Handles:
        - Access token from cookie
        - Token validation
        - Optional refresh token helper
    """
    access_cookie_name: str = None
    refresh_cookie_name: str = None

    def authenticate(self, request):
        raw_token = request.COOKIES.get(self.access_cookie_name)
        logger.info(f"[CookieJWT] Raw token from cookie '{self.access_cookie_name}': {raw_token}")

        if not raw_token:
            logger.info(f"[CookieJWT] No {self.access_cookie_name} found in cookies.")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            if user is None:
                logger.warning(f"[CookieJWT] Token validated but no user found for ID: {validated_token.get('user_id')}")
                return None
            logger.info(f"[CookieJWT] Token validated successfully for user ID: {user.id}")
            return user, validated_token
        except TokenError as e:
            logger.warning(f"[CookieJWT] Invalid access token in cookie: {e}")
            return None

    def authenticate_header(self, request):
        return 'Bearer'

    def refresh_access_token(self, request):
        """
        Refresh access token using refresh cookie.
        Returns new access token string if successful, else None.
        """
        refresh_token = request.COOKIES.get(self.refresh_cookie_name)
        logger.info(f"[CookieJWT] Raw refresh token from cookie '{self.refresh_cookie_name}': {refresh_token}")

        if not refresh_token:
            logger.info(f"[CookieJWT] No {self.refresh_cookie_name} found in cookies.")
            return None

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
            logger.info(f"[CookieJWT] Refresh token validated. New access token generated.")
            return new_access
        except TokenError as e:
            logger.warning(f"[CookieJWT] Invalid refresh token in cookie: {e}")
            return None





class UserCookieJWTAuthentication(BaseCookieJWTAuthentication):
    access_cookie_name = "user_access_token"
    refresh_cookie_name = "user_refresh_token"

    def get_user(self, validated_token):
        from users.models.user_model import User
        try:
            user_id = validated_token["user_id"]
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f"[UserCookieJWT] No User found with ID: {validated_token.get('user_id')}")
            return None







class CompanyCookieJWTAuthentication(BaseCookieJWTAuthentication):
    access_cookie_name = "company_access_token"
    refresh_cookie_name = "company_refresh_token"

    def get_user(self, validated_token):
        from company.models.company_model import Company
        try:
            user_id = validated_token["user_id"]
            return Company.objects.get(pk=user_id)
        except Company.DoesNotExist:
            logger.warning(f"[CompanyCookieJWT] No Company found with ID: {validated_token.get('user_id')}")
            return None
