from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404

from .models import  Category, Product, SubCategory
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db.models import Sum, F

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm



from django.core.mail import send_mail
from django.urls import reverse
import uuid








def homepage(request):
    return render(request, 'homepage.html')



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            try:
                # Create the user
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('products')
            except Exception as e:
                # Handle any exceptions during user creation
                error_message = "An error occurred while registering the user. Please try again."
                return render(request, 'register.html', {'form': form, 'error_message': error_message})
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        logout(request)  # Logout any user already logged in
    
    if request.method == 'POST':
        username = request.POST['username']  # Use 'username' instead of 'email'
        password = request.POST['password']
        
        # Authenticate using username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to the previous page or 'home' if not available
            return redirect(request.GET.get('next', 'products'))  
        else:
            # Handle authentication failure
            error_message = "Invalid username or password. Please try again."
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)  # This logs out the user
    return redirect('home')  





@login_required
def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    subcategories = SubCategory.objects.filter(category=category)
    
    # Retrieve search query from GET parameters
    query = request.GET.get('q')
    
    # Retrieve minimum and maximum price values from GET parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Convert min_price and max_price to Decimal if they are not None and not empty strings
    if min_price is not None and min_price != '':
        min_price = Decimal(min_price)
    else:
        min_price = None
    if max_price is not None and max_price != '':
        max_price = Decimal(max_price)
    else:
        max_price = None
    
    # Calculate cart count for the current user's cart
    cart_products = Product.objects.filter(cart_quantity__gt=0)
    cart_count = cart_products.aggregate(Sum('cart_quantity'))['cart_quantity__sum'] or 0
    
    # Filter products by category and subcategory
    products_by_subcategory = []
    for subcategory in subcategories:
        products = Product.objects.filter(category=category, subcategory=subcategory)
        
        # If query exists, filter products by name or description
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        # Filter products by price range
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        
        products_by_subcategory.append({'subcategory': subcategory, 'products': products})
        
    # Pass the search results to the template if a query exists
    if query:
        search_results = [product for subcategory_data in products_by_subcategory for product in subcategory_data['products']]
        return render(request, 'product_list.html', {'category': category, 'search_results': search_results, 'min_price': min_price, 'max_price': max_price, 'cart_count': cart_count})
    
    return render(request, 'product_list.html', {'category': category, 'products_by_subcategory': products_by_subcategory, 'min_price': min_price, 'max_price': max_price, 'cart_count': cart_count})


def product_list_by_subcategory(request, category_id, subcategory_id):
    category = get_object_or_404(Category, pk=category_id)
    subcategory = get_object_or_404(SubCategory, pk=subcategory_id)
    cart_products = Product.objects.filter(cart_quantity__gt=0)
    # Calculate total cart count
    cart_count = cart_products.aggregate(Sum('cart_quantity'))['cart_quantity__sum'] or 0
    # Get the search query from the request parameters
    query = request.GET.get('q')

    # Filter products based on category, subcategory, and search query
    products = Product.objects.filter(category=category, subcategory=subcategory)
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'product_list.html', {'category': category, 'subcategory': subcategory, 'products': products, 'cart_count': cart_count})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def display_two_products(request):
    cart_products = Product.objects.filter(cart_quantity__gt=0)
    # Calculate total cart count
    cart_count = cart_products.aggregate(Sum('cart_quantity'))['cart_quantity__sum'] or 0
    categories = Category.objects.all()
    category_products = []
    for category in categories:
        products = Product.objects.filter(category=category)[:4]  # Retrieve some products per category
        category_products.append({'category': category, 'products': products})
    return render(request, 'display_two_products.html', {'category_products': category_products, 'cart_count': cart_count})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    # Get the quantity from the request POST data
    quantity = int(request.POST.get('quantity', 1))

    # Read the existing cart quantity
    current_cart_quantity = product.cart_quantity

    # Reduce product stock if available
    if product.stock >= quantity:
        product.stock -= quantity
        product.save()

        # Update cart quantity based on existing value
        product.cart_quantity = current_cart_quantity + quantity
        product.save()

    # Redirect the user back to the previous page (current page)
    return redirect(request.META.get('HTTP_REFERER', '/'))



@login_required
def cart_detail(request):
    # Fetch products with non-zero cart quantity for the logged-in user
    cart_products = Product.objects.filter(cart_quantity__gt=0)

    # Calculate total cart count
    cart_count = cart_products.aggregate(Sum('cart_quantity'))['cart_quantity__sum'] or 0
    
    # Calculate subtotal for each product and total price
    total_price = sum(product.price * product.cart_quantity for product in cart_products)
    
    # Calculate subtotal for each product
    for product in cart_products:
        product.subtotal = product.price * product.cart_quantity

    return render(request, 'cart_detail.html', {'cart_products': cart_products, 'total_price': total_price, 'cart_count': cart_count})


@login_required
def checkout(request):
    user = request.user
    email = user.email

    # Process checkout logic here...
    
    # Calculate total price
    cart_products = Product.objects.filter(cart_quantity__gt=0)
    total_price = sum(product.price * product.cart_quantity for product in cart_products)

    # Send email notification with total price
    send_email(email, "Order Confirmation", f"Your order has been placed successfully! Total Price: ${total_price}")

    # Send SMS notification (using a suitable SMS service)

    # Clear the cart
    Product.objects.filter(cart_quantity__gt=0).update(cart_quantity=0)

    return redirect('payment_process')


def send_email(email, subject, message):
    try:
        # Send email using SMTP server
        send_mail(subject, message, 'ndrwrono2001@gmail.com', [email])
        return True  # Email sent successfully
    except Exception as e:
        print(f"Error sending email: {e}")
        return False  # Email sending failed

@csrf_exempt
def payment_process(request):
    # Fetch products with non-zero cart quantity for the logged-in user
    cart_products = Product.objects.filter(cart_quantity__gt=0)
    
    print("Cart products:", cart_products)

    # Calculate total price based on products in the cart
    total_price = sum(product.price * product.cart_quantity for product in cart_products)
    
    print("Total price:", total_price)


    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total_price,
        'currency_code': 'USD',
        'item_name': 'Purchase',
        'invoice': uuid.uuid4(),
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('payment_done')}",
        'cancel_url': f"http://{host}{reverse('payment_canceled')}",
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'process.html', {'form': form, 'total_price': total_price})
@csrf_exempt
def payment_done(request):
    return redirect('products')

@csrf_exempt
def payment_canceled(request):
    return render(request, 'canceled.html')
