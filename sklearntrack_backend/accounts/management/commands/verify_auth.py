# FILE: accounts/management/commands/verify_auth.py
# Create directory: accounts/management/commands/
# Run with: python manage.py verify_auth
# ============================================================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class Command(BaseCommand):
    help = 'Verify authentication system is working correctly'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Authentication System Verification ===\n'))

        # Check settings
        self.verify_settings()

        # Check existing users
        self.check_users()

        # Test authentication
        self.test_authentication()

        self.stdout.write(self.style.SUCCESS('\n=== Verification Complete ===\n'))

    def verify_settings(self):
        self.stdout.write(self.style.WARNING('\n1. Checking Settings...'))

        # Check AUTH_USER_MODEL
        if settings.AUTH_USER_MODEL == 'accounts.User':
            self.stdout.write(self.style.SUCCESS('   ✓ AUTH_USER_MODEL is correctly set'))
        else:
            self.stdout.write(self.style.ERROR(f'   ✗ AUTH_USER_MODEL is {settings.AUTH_USER_MODEL}'))

        # Check AUTHENTICATION_BACKENDS
        backends = settings.AUTHENTICATION_BACKENDS
        if 'accounts.backends.EmailBackend' in backends:
            self.stdout.write(self.style.SUCCESS('   ✓ EmailBackend is configured'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ EmailBackend is not configured'))

        # Check SIMPLE_JWT
        if hasattr(settings, 'SIMPLE_JWT'):
            self.stdout.write(self.style.SUCCESS('   ✓ JWT settings are configured'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ JWT settings are missing'))

    def check_users(self):
        self.stdout.write(self.style.WARNING('\n2. Checking Users...'))

        user_count = User.objects.count()
        self.stdout.write(f'   Total users: {user_count}')

        if user_count > 0:
            self.stdout.write('\n   User List:')
            for user in User.objects.all()[:10]:
                role_badge = '👑' if user.role == 'admin' else '👤'
                self.stdout.write(
                    f'   {role_badge} {user.email} | '
                    f'Role: {user.role} | '
                    f'Staff: {user.is_staff} | '
                    f'Active: {user.is_active}'
                )

    def test_authentication(self):
        self.stdout.write(self.style.WARNING('\n3. Testing Authentication...'))

        # Create test user if not exists
        test_email = 'test_verify@example.com'
        test_password = 'TestPass123!'

        try:
            # Try to get existing user
            user = User.objects.get(email=test_email)
            self.stdout.write(f'   Using existing test user: {test_email}')
        except User.DoesNotExist:
            # Create new test user
            user = User.objects.create_user(
                email=test_email,
                password=test_password,
                full_name='Test User',
                country='USA',
                education_level='undergraduate',
                field_of_study='Computer Science',
                terms_accepted=True
            )
            self.stdout.write(self.style.SUCCESS(f'   ✓ Created test user: {test_email}'))

        # Test authentication
        auth_user = authenticate(email=test_email, password=test_password)
        if auth_user:
            self.stdout.write(self.style.SUCCESS('   ✓ Authentication successful'))
            self.stdout.write(f'   User: {auth_user.email}')
            self.stdout.write(f'   Role: {auth_user.role}')
            self.stdout.write(f'   Username: {auth_user.username}')

            # Test JWT token generation
            try:
                refresh = RefreshToken.for_user(auth_user)
                self.stdout.write(self.style.SUCCESS('   ✓ JWT token generation successful'))
                self.stdout.write(f'   Access Token Length: {len(str(refresh.access_token))} chars')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ JWT token generation failed: {e}'))

        else:
            self.stdout.write(self.style.ERROR('   ✗ Authentication failed'))

        # Test with wrong password
        wrong_auth = authenticate(email=test_email, password='WrongPassword123!')
        if wrong_auth is None:
            self.stdout.write(self.style.SUCCESS('   ✓ Wrong password correctly rejected'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ Wrong password was accepted!'))

        # Test with non-existent email
        fake_auth = authenticate(email='nonexistent@example.com', password='AnyPassword123!')
        if fake_auth is None:
            self.stdout.write(self.style.SUCCESS('   ✓ Non-existent email correctly rejected'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ Non-existent email was accepted!'))

        # Cleanup test user
        if User.objects.filter(email=test_email).exists():
            self.stdout.write(f'\n   Test user {test_email} kept for further testing')
            self.stdout.write(f'   Password: {test_password}')