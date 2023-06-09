from django.core.management.base import BaseCommand, CommandError
from simpleapp.models import Post

class Command(BaseCommand):
    help = 'меняет описание всех товаров на wow'

    def handle(self, *args, **options):
        for post in Post.objects.all():
            post.description = 'wow'
            post.save()

            self.stdout.write(self.style.SUCCESS('Successfuly nulled post "%s"' %str(post)))