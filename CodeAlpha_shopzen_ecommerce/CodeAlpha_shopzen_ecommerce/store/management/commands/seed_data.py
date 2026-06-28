from django.core.management.base import BaseCommand
from store.models import Category, Product
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Seed the database with sample products'

    def handle(self, *args, **kwargs):
        # Categories
        categories_data = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']
        categories = {}
        for name in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            categories[name] = cat
            self.stdout.write(f'  Category: {name}')

        # Products
        products = [
            {'name': 'Wireless Headphones Pro', 'category': 'Electronics', 'price': 89.99, 'stock': 25, 'description': 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear sound.'},
            {'name': 'Smart Watch Series X', 'category': 'Electronics', 'price': 249.00, 'stock': 15, 'description': 'Track your fitness, receive notifications, and monitor your health with this advanced smartwatch.'},
            {'name': 'Bluetooth Speaker Mini', 'category': 'Electronics', 'price': 39.99, 'stock': 40, 'description': 'Compact waterproof Bluetooth speaker with 360° sound and 12-hour battery.'},
            {'name': 'USB-C Hub 7-in-1', 'category': 'Electronics', 'price': 49.99, 'stock': 30, 'description': 'Expand your laptop with HDMI, USB 3.0, SD card reader, and more.'},
            {'name': 'Classic Crew Neck Tee', 'category': 'Clothing', 'price': 19.99, 'stock': 100, 'description': '100% organic cotton crew neck t-shirt. Soft, comfortable, and sustainable.'},
            {'name': 'Slim Fit Chinos', 'category': 'Clothing', 'price': 54.99, 'stock': 60, 'description': 'Modern slim fit chinos made from stretch cotton blend. Perfect for casual and smart casual occasions.'},
            {'name': 'Minimalist Hoodie', 'category': 'Clothing', 'price': 69.99, 'stock': 45, 'description': 'French terry cotton hoodie with clean lines and a relaxed silhouette.'},
            {'name': 'Clean Code', 'category': 'Books', 'price': 34.99, 'stock': 20, 'description': 'A handbook of agile software craftsmanship by Robert C. Martin. Essential reading for developers.'},
            {'name': 'The Art of War', 'category': 'Books', 'price': 9.99, 'stock': 50, 'description': 'Sun Tzu\'s ancient Chinese military treatise, applicable to business and life strategy.'},
            {'name': 'Deep Work', 'category': 'Books', 'price': 16.99, 'stock': 35, 'description': 'Cal Newport\'s guide to focused success in a distracted world.'},
            {'name': 'Succulent Plant Set', 'category': 'Home & Garden', 'price': 24.99, 'stock': 30, 'description': 'Set of 4 easy-care succulent plants in terracotta pots. Perfect for home or office.'},
            {'name': 'Scented Candle Collection', 'category': 'Home & Garden', 'price': 32.00, 'stock': 40, 'description': 'Set of 3 hand-poured soy wax candles: Vanilla, Cedarwood, and Fresh Linen.'},
            {'name': 'Yoga Mat Premium', 'category': 'Sports', 'price': 45.00, 'stock': 25, 'description': '6mm thick non-slip yoga mat with carry strap. Eco-friendly TPE material.'},
            {'name': 'Resistance Bands Set', 'category': 'Sports', 'price': 28.99, 'stock': 50, 'description': 'Set of 5 resistance bands with different tension levels. Great for home workouts.'},
            {'name': 'Water Bottle Insulated', 'category': 'Sports', 'price': 22.99, 'stock': 60, 'description': 'Double-wall stainless steel insulated water bottle. Keeps drinks cold 24h, hot 12h.'},
        ]

        for p in products:
            slug = slugify(p['name'])
            obj, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': p['name'],
                    'category': categories[p['category']],
                    'price': p['price'],
                    'stock': p['stock'],
                    'description': p['description'],
                }
            )
            if created:
                self.stdout.write(f'  Product: {p["name"]}')

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data seeded successfully!'))
        self.stdout.write('  → Create a superuser: python manage.py createsuperuser')
        self.stdout.write('  → Then visit: http://localhost:8000/')
