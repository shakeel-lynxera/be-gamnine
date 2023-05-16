import random
from pyfcm import FCMNotification
from gemnineDealerBackend.settings import FCM_API_KEY
from user_deals.models import Property, PropertyPurpose


#gemnine method reuseablity
def generate_six_length_random_number():
    random_otp = random.SystemRandom().randint(100000,999999)
    return str(random_otp)

#Firebase notification method
def send_firebase_notification(message_title, message_body, registration_ids, extra_notification_kwargs=None):
    try:
        push_service = FCMNotification(api_key=FCM_API_KEY)
        response = push_service.notify_multiple_devices(registration_ids=registration_ids,
                                             message_body = message_body, message_title=message_title,
                                             extra_notification_kwargs = extra_notification_kwargs,
                                             sound = "gemnine-notification-sound.caf")
        return response
    except Exception as e:
        print(f"Error in sending notification: {e}")

def configure_firebase_notification(ticket):
    if ticket.purpose == "sale":
        purpose = "required"
    else:
        purpose = "sale"
    fcm_token_list = Property.objects.filter(type=ticket.type,
                                             city__icontains=ticket.city,
                                             location__icontains=ticket.location,
                                             purpose = purpose)\
                                    .exclude(id=ticket.id)\
                                    .values_list('user__fcm_token', flat=True)
    fcm_token_list = list(dict().fromkeys(fcm_token_list))
    if len(fcm_token_list) > 0:
        extra_notification_kwargs = {
            "sound": "gemnine-notification-sound.caf",
            "badge": "1",
            "click_action": "FCM_PLUGIN_ACTIVITY",
            "icon": "fcm_push_icon",
            "tag": "gemnine-notification-tag",
            "color": "red",
            "ticket_id": ticket.id
        }
    send_firebase_notification(
        message_title="Similar deal available",
        message_body=ticket.title,
        registration_ids=fcm_token_list,
        extra_notification_kwargs=extra_notification_kwargs
    )
