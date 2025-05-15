from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('author', 'category',)
    list_display_links = ('title',)
    empty_value_display = 'Не задано'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    empty_value_display = 'Не задано'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    empty_value_display = 'Не задано'
