from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404
from .models import  Category, Product, SubCategory
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.db.models import Q




def homepage(request):
    return render(request, 'homepage.html')



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                # Create the user
                user = User.objects.create_user(username=username, password=password)
                # Log in the user
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


# Create your views here.
def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    subcategories = SubCategory.objects.filter(category=category)
    
    # Retrieve search query from GET parameters
    query = request.GET.get('q')
    
    # Retrieve minimum and maximum price values from GET parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
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
        return render(request, 'product_list.html', {'category': category, 'search_results': search_results, 'min_price': min_price, 'max_price': max_price})
    
    return render(request, 'product_list.html', {'category': category, 'products_by_subcategory': products_by_subcategory, 'min_price': min_price, 'max_price': max_price})

def product_list_by_subcategory(request, category_id, subcategory_id):
    category = get_object_or_404(Category, pk=category_id)
    subcategory = get_object_or_404(SubCategory, pk=subcategory_id)
    
    # Get the search query from the request parameters
    query = request.GET.get('q')

    # Filter products based on category, subcategory, and search query
    products = Product.objects.filter(category=category, subcategory=subcategory)
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'product_list.html', {'category': category, 'subcategory': subcategory, 'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})


def display_two_products(request):
    categories = Category.objects.all()
    category_products = []
    for category in categories:
        products = Product.objects.filter(category=category)[:4]  # Retrieve some products per category
        category_products.append({'category': category, 'products': products})
    return render(request, 'display_two_products.html', {'category_products': category_products})



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    # Get the quantity from the request POST data
    quantity = int(request.POST.get('quantity', 1))  # Default to 1 if quantity is not specified
    
    # Update cart quantity for the product
    product.cart_quantity = quantity
    product.save()

    # Redirect to cart detail page
    return redirect('cart_detail')

def cart_detail(request):
    # Fetch products with non-zero cart quantity
    cart_products = Product.objects.filter(cart_quantity__gt=0)
    
    # Calculate subtotal for each product and total price
    total_price = 0
    for product in cart_products:
        product.subtotal = product.price * product.cart_quantity  # Calculate subtotal for the product
        total_price += product.subtotal  # Accumulate subtotal to calculate total price

    return render(request, 'cart_detail.html', {'cart_products': cart_products, 'total_price': total_price})
