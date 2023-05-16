from django.db import models
from baselayer.basemodels import LogsMixin
from django.contrib.auth.models import AbstractUser
from baselayer.baseauthentication import generate_access_token

#Choice classes
class PhoneNumberOTPTypeChoices(models.TextChoices):
    signup_otp = "signup_otp", 'Signup OTP'
    forgot_password_otp = "forgot_password_otp", 'Forgot Password OTP'
    change_number_otp = "change_number_otp", 'Change Number OTP'

# Create your models here.

class User(LogsMixin, AbstractUser):
    """Fully featured User model with admin-compliant permissions.
    email and password are required. Other fields are optional.
    """

    email = models.EmailField(("email address"), blank=True, null=True)
    phone_number = models.CharField(("phone number"), max_length=15, unique=True)
    fullname = models.CharField(("full name"), max_length=50, blank=True, null=True)
    is_active = models.BooleanField(("is_active"), default=False)
    fcm_token = models.TextField(blank=True, null=True)
    # token = models.TextField(_('token'), unique=True)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email", "password"]
    # Remove below username, first_name and last_name from user model
    username = None
    first_name = None
    last_name = None

    def get_access_token(self):
        return generate_access_token(self)


class UserProfile(LogsMixin):
    city = models.CharField(max_length=50, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class PhoneNumberOTP(LogsMixin):
    twilio_service_id = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    otp_type = models.CharField(choices=PhoneNumberOTPTypeChoices.choices,
                                default=PhoneNumberOTPTypeChoices.signup_otp,
                                max_length=50)
    user = models.ForeignKey(
        User, related_name="phone_number_otp", on_delete=models.CASCADE
    )

class TempUserEmail(LogsMixin):
    email = models.EmailField(("email address"), blank=True, null=True)
    otp = models.CharField(("otp"), max_length=6)
    user = models.ForeignKey(
        User, related_name="temp_user_email", on_delete=models.CASCADE
    )
