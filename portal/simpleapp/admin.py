from django.contrib import admin
from .models import Category, Post, Author, PostCategory

class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'createDate')

admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Author)
admin.site.register(PostCategory)

