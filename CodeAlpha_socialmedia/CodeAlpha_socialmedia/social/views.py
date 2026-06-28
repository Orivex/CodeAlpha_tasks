from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Comment, Like, Follow, Profile
from .forms import UserRegistrationForm, UserLoginForm, PostForm, CommentForm, ProfileUpdateForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to SocialHub, {user.username}!')
            return redirect('feed')
    else:
        form = UserRegistrationForm()
    return render(request, 'social/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'social/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def feed_view(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(author__in=list(following_users) + [request.user.id]).select_related('author', 'author__profile')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('feed')
    else:
        form = PostForm()

    # Add like status to posts
    for post in posts:
        post.liked_by_user = post.is_liked_by(request.user)

    # Suggested users (not followed, not self)
    followed_ids = list(following_users) + [request.user.id]
    suggested = User.objects.exclude(id__in=followed_ids).select_related('profile')[:5]

    return render(request, 'social/feed.html', {
        'posts': posts,
        'form': form,
        'suggested': suggested,
    })


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).select_related('author', 'author__profile')
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    for post in posts:
        post.liked_by_user = post.is_liked_by(request.user)

    return render(request, 'social/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile_user.profile.get_followers_count(),
        'following_count': profile_user.profile.get_following_count(),
        'posts_count': profile_user.profile.get_posts_count(),
    })


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            # Update user fields
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'social/edit_profile.html', {'form': form})


@login_required
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author', 'author__profile').all()
    post.liked_by_user = post.is_liked_by(request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'author': comment.author.username,
                        'content': comment.content,
                        'created_at': comment.created_at.strftime('%b %d, %Y'),
                        'avatar_url': comment.author.profile.avatar.url if comment.author.profile.avatar else '',
                    }
                })
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()

    return render(request, 'social/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.get_likes_count()})


@login_required
@require_POST
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow.delete()
        following = False
    else:
        following = True

    return JsonResponse({
        'following': following,
        'followers_count': target_user.profile.get_followers_count()
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('feed')


@login_required
def search_view(request):
    query = request.GET.get('q', '')
    users = []
    posts = []
    if query:
        users = User.objects.filter(username__icontains=query).select_related('profile').exclude(id=request.user.id)[:10]
        posts = Post.objects.filter(content__icontains=query).select_related('author', 'author__profile')[:20]
        for post in posts:
            post.liked_by_user = post.is_liked_by(request.user)
    return render(request, 'social/search.html', {'users': users, 'posts': posts, 'query': query})


@login_required
def followers_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=profile_user).select_related('follower', 'follower__profile')
    return render(request, 'social/followers.html', {'profile_user': profile_user, 'followers': followers, 'tab': 'followers'})


@login_required
def following_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=profile_user).select_related('following', 'following__profile')
    return render(request, 'social/followers.html', {'profile_user': profile_user, 'following': following, 'tab': 'following'})
