# FILE: accounts/backends.py
# ============================================================================

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailBackend(ModelBackend):
    """Custom authentication backend that uses email instead of username"""
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate user using email and password
        """
        if email is None or password is None:
            return None

        try:
            # Normalize email to lowercase and strip whitespace
            email = email.lower().strip()
            
            # Find user by email
            user = User.objects.get(email=email)
            
            # Check password and if user can authenticate
            if user.check_password(password) and self.user_can_authenticate(user):
                logger.info(f"Authentication successful for: {email}")
                return user
            else:
                logger.warning(f"Authentication failed for: {email} (invalid password or inactive)")
                return None
                
        except User.DoesNotExist:
            logger.warning(f"Authentication failed for: {email} (user not found)")
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user
            User().set_password(password)
            return None
        except Exception as e:
            logger.error(f"Authentication error for {email}: {str(e)}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            user = User.objects.get(pk=user_id)
            return user if self.user_can_authenticate(user) else None
        except User.DoesNotExist:
            return None