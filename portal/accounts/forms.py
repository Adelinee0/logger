from django import forms
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django.core.mail import send_mail,  mail_admins, mail_managers


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        subject='Добро пожаловать в наш NEWS PORTAL!'
        text=f'{user.username}, вы успешно зарегистрировались!'
        html=f'<b>{user.username}</b>, вы успешно зарегистрировались на 'f'<a href="http://127.0.0.1:8000/posts">сайте</a>!'
        msg = EmailMultiAlternatives(
                subject=subject, body=text,
                from_email=None,
                to=[user.email])
        msg.attach_alternative(html, "text/html")
        msg.send()



        mail_managers(
            subject='Новый author!',
            message=f'Пользователь {user.username} зарегистрировался на сайте.'
        )

        mail_admins(
            subject='Новый пользователь!',
            message=f'Пользователь {user.username} зарегистрировался на сайте.'
        )

        common_users = Group.objects.get(name="common users")
        user.groups.add(common_users)

        return user