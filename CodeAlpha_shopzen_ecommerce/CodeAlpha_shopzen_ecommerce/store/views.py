from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Order, OrderItem, Review
from .forms import CheckoutForm, ReviewForm, RegisterForm
import json
from decimal import Decimal


# ── Cart helpers (session-based) ──────────────────────────────────────────────

def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


# ── Public pages ──────────────────────────────────────────────────────────────

def home(request):
    featured = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'featured': featured, 'categories': categories})


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    search = request.GET.get('q')
    sort = request.GET.get('sort', 'newest')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'search': search,
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            r = review_form.save(commit=False)
            r.product = product
            r.user = request.user
            r.save()
            messages.success(request, 'Review submitted!')
            return redirect('product_detail', slug=slug)

    avg_rating = None
    if reviews.exists():
        avg_rating = round(sum(r.rating for r in reviews) / reviews.count(), 1)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'related': related,
        'review_form': review_form,
        'avg_rating': avg_rating,
    })


# ── Cart views ────────────────────────────────────────────────────────────────

def cart_view(request):
    cart = get_cart(request)
    cart_items = []
    total = Decimal('0')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        except Product.DoesNotExist:
            pass
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


def add_to_cart(request, product_id):
    cart = get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    save_cart(request, cart)
    messages.success(request, 'Item added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def remove_from_cart(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)
    return redirect('cart')


def update_cart(request, product_id):
    cart = get_cart(request)
    qty = int(request.POST.get('quantity', 1))
    if qty > 0:
        cart[str(product_id)] = qty
    else:
        cart.pop(str(product_id), None)
    save_cart(request, cart)
    return redirect('cart')


# ── Checkout & orders ─────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    cart_items = []
    total = Decimal('0')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data['country'],
                total_amount=total,
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price,
                )
                # Reduce stock
                p = item['product']
                p.stock = max(0, p.stock - item['quantity'])
                p.save()

            # Clear cart
            request.session['cart'] = {}
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
        })

    return render(request, 'store/checkout.html', {
        'form': form, 'cart_items': cart_items, 'total': total
    })


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# ── Auth ──────────────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'store/profile.html', {'orders': orders})
