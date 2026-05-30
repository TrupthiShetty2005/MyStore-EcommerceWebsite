from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product, Category
from .cart import Cart

# 1. ADVANCED STOREFRONT SEARCH & FILTER VIEW
def product_list(request):
    """View to display the product catalog with search, category, and price filters."""
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    # Capture Search Queries
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    # Capture Category Filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Capture Price Filters
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'category_slug': category_slug,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop/list.html', context)


# 2. ADD TO CART VIEW
@require_POST
def cart_add(request, product_id):
    """View to handle adding items to the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)
    return redirect('cart_detail')


# 3. REMOVE FROM CART VIEW
def cart_remove(request, product_id):
    """View to handle removing items."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


# 4. CART DETAILS SUMMARY VIEW (The missing function!)
def cart_detail(request):
    """View to display the cart page."""
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})

# Add these functions to the very bottom of your shop/views.py file

def wishlist_toggle(request, product_id):
    """Adds an item to the wishlist if it's not there, or removes it if it is."""
    product = get_object_or_404(Product, id=product_id)
    
    # Initialize wishlist in session if it doesn't exist
    if 'wishlist' not in request.session:
        request.session['wishlist'] = []
        
    wishlist = request.session['wishlist']
    
    if product_id in wishlist:
        wishlist.remove(product_id) # Remove if already liked
    else:
        wishlist.append(product_id) # Add if new
        
    request.session.modified = True
    
    # Redirect back to whichever page the user was looking at
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


def wishlist_detail(request):
    """Displays the user's personal wishlisted items."""
    categories = Category.objects.all()
    wishlist_ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids, available=True)
    
    return render(request, 'shop/list.html', {
        'products': products,
        'categories': categories,
        'is_wishlist_page': True # Flag to change the title heading
    })