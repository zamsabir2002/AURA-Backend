# utils.py
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import UserActivityLog, User

def check_for_unusual_activity(user):
    time_threshold = timezone.now() - timedelta(minutes=15)
    recent_activities = UserActivityLog.objects.filter(user=user, activity_type='login', timestamp__gte=time_threshold).count()

    if recent_activities > 5:  # Threshold for unusual activity
        send_alert_email_to_admins(user)

def send_alert_email_to_admins(user):
    admins = User.objects.filter(role = 1)
    subject = 'Unusual Activity Detected'
    message = f'Unusual login activity detected for User Name: {user.name} and Email: {user.email}.\nMultiple login attempts in a short period.\n\nBest Regard,\nTeam AURA'
    for admin in admins:
        send_mail(subject, message, 'aura.riskdashboard@gmail.com', [admin.email])
