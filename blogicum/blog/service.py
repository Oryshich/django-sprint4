from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.constants import POSTS_ON_PAGE
from blog.models import Post


def query_set(filter=None, annotate=None):
    query_set = Post.objects.select_related(
        'category',
        'location',
        'author'
    )
    if filter:
        query_set = query_set.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if annotate:
        query_set = query_set.annotate(
            comment_count=Count('comments')
        )
    return query_set.order_by('-pub_date')


def get_paginator(request, queryset, number_of_pages=POSTS_ON_PAGE):
    paginator = Paginator(queryset, number_of_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
