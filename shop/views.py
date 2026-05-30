from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Product, Category
from .cart import Cart

# 1. ADVANCED STOREFRONT SEARCH & FILTER VIEW
# 1. ADVANCED STOREFRONT SEARCH & FILTER VIEW
def product_list(request):
    """View to display the product catalog with search, category, and price filters."""
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    # Capture Search Queries
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')

    if query:
        # If searching by text, check name, description, or category name
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
        # OPTIMIZATION: If someone types a fresh text search, reset the restrictive 
        # category slug filter so it doesn't accidentally cancel out their search results.
        category_slug = '' 
        
    elif category_slug:
        # Otherwise, if no text search, filter strictly by selected category dropdown/sidebar
        products = products.filter(category__slug=category_slug)

    # Capture Price Filters (remain active for filtering search results)
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


# 4. CART DETAILS SUMMARY VIEW
def cart_detail(request):
    """View to display the cart page."""
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


# 5. WISHLIST TOGGLE VIEW
def wishlist_toggle(request, product_id):
    """Adds an item to the wishlist if it's not there, or removes it if it is."""
    product = get_object_or_404(Product, id=product_id)
    
    if 'wishlist' not in request.session:
        request.session['wishlist'] = []
        
    wishlist = request.session['wishlist']
    
    if product_id in wishlist:
        wishlist.remove(product_id)
    else:
        wishlist.append(product_id)
        
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


# 6. WISHLIST DETAIL VIEW
def wishlist_detail(request):
    """Displays the user's personal wishlisted items."""
    categories = Category.objects.all()
    wishlist_ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids, available=True)
    
    return render(request, 'shop/list.html', {
        'products': products,
        'categories': categories,
        'is_wishlist_page': True
    })