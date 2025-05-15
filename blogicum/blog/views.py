from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import UpdateView

from blog.forms import (
    CommentForm, PostForm, EditUserProfileForm
)
from blog.models import Category, Post, Comment


POSTS_ON_PAGE = 10


User = get_user_model()


def logout_view(request):
    logout(request)
    return render(request, 'registration/logged_out.html')


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
        ).order_by('-pub_date')
    return query_set


def get_paginator(request, queryset, number_of_pages=POSTS_ON_PAGE):
    paginator = Paginator(queryset, number_of_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = query_set(filter=True, annotate=True)
    page_obj = get_paginator(request, post_list, POSTS_ON_PAGE)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    """Для просмотра сгруппированных записей по категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = query_set(filter=True, annotate=True).filter(category=category)
    page_obj = get_paginator(request, post_list, POSTS_ON_PAGE)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile = get_object_or_404(
        User.objects.all().filter(
            username=username
        )
    )
    post_list = Post.objects.select_related(
        'author',
        'location',
        'category'
    ).filter(author=profile).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        query_set(filter=False, annotate=False),
        id=post_id
    )
    if request.user != post.author:
        post = get_object_or_404(
            query_set(filter=True, annotate=False),
            id=post_id,
        )
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related('author').filter(post=post)
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, 'blog/detail.html', context)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditUserProfileForm
    template_name = "blog/user.html"

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment,
               'form': form}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
