from django.urls import path
from users.views import (RegistrationView,
                         SignInView,
                         ForgetPasswordAPIView,
                         VerifyOTPAPIView,
                         ResetPasswordAPIView,
                         ProfileView,
                         EmailView,
                         PhoneNumberView,
                         PasswordAPIView,
                         VerifyEmailOTPView,
                         )

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="register-new-user"),
    path("sign-in/", SignInView.as_view(), name="sign-in-user"),
    #Forgot Password
    path("forget-password/", ForgetPasswordAPIView.as_view(), name="forget-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    #Verify OTP (Forgot Password, Change Phone Number and Sign up)
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),
    #Profile Settings
    path("profile/", ProfileView.as_view(), name ="update-name"),
    path("change-email/", EmailView.as_view(), name ="update email"),
    path("verify-email-otp/", VerifyEmailOTPView.as_view(), name ="verify-email-otp"),
    path("change-phone-number/", PhoneNumberView.as_view(), name ="update_number"),
    path("change-password/", PasswordAPIView.as_view(), name="update-password"),
]
