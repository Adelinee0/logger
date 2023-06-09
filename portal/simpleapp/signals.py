
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from portal.settings import SITE_URL, DEFAULT_FROM_EMAIL
from django.template.loader import render_to_string
from .models import Post, Category

def send_notifications(preview, pk, name, subscribers):
    html_content = render_to_string(
        'post_created_emails.html',
        {
            'text': preview,
            'link': f'{SITE_URL}/news/{pk}',
        }

    )

    msg = EmailMultiAlternatives(
        subject=name,
        body='',
        from_email=DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@receiver(post_save, sender=Post)
def notify_about_new_post(sender, instance, created, **kwargs):
    print('Signal1')
    print(kwargs)
    if created:
        print('Signal2')
        categories = instance.category
        subscribers: list[str] = []
        subscribers += categories.subscribers.all()

        subscribers = [s.email for s in subscribers]
        print('Subscribers')

        send_notifications(instance.preview(),
                           instance.pk, instance.name, subscribers)




