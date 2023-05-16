from twilio.rest import Client
from gemnineDealerBackend.settings import (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

COMPANY_NAME = "Gemnine Technologies"


def get_twilio_client():
    """Get twilio client using TWILIO_ACCOUNT_SID, and TWILIO_AUTH_TOKEN"""
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


client = get_twilio_client()


def send_phone_number_verification_sms(phone_number):
    """Send phone number verification code sms
    :param phone_number
    :return service
    :return custom_friendly_name
    """
    service = client.verify.services.create(friendly_name=COMPANY_NAME)
    client.verify.services(service.sid).verifications.create(
        to=phone_number, channel="sms"
    )
    return service


def verify_phone_number_with_otp(service_id, phone_number, otp):
    return client.verify.services(service_id).verification_checks.create(to=phone_number, code=otp)

"""def send_email_verification_code(email):

    service = client.verify.services.create(friendly_name=COMPANY_NAME)
    client.verify.services(service.sid).verifications.create(
        to=phone_number, channel="email"
    )
    return service

def verify_email_with_otp(service_id, email, otp):
    return client.verify.services(service_id).verification_checks.create(to=email, code=otp)"""

