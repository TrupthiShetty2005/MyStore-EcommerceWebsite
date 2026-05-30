from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart using Django sessions."""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Save an empty cart in the session if none exists
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Mark the session as "modified" to make sure it saves to the browser
        self.session.modified = True

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        """Calculate the total cost of all items in the cart."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Empty the cart session."""
        del self.session['cart']
        self.save()