from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404
from .models import  Category, Product, SubCategory
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm
from django.contrib.auth.models import User



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
    products_by_subcategory = []
    for subcategory in subcategories:
        products = Product.objects.filter(category=category, subcategory=subcategory)
        products_by_subcategory.append({'subcategory': subcategory, 'products': products})
    return render(request, 'product_list.html', {'category': category, 'products_by_subcategory': products_by_subcategory})

def product_list_by_subcategory(request, category_id, subcategory_id):
    category = get_object_or_404(Category, pk=category_id)
    subcategory = get_object_or_404(SubCategory, pk=subcategory_id)
    products = Product.objects.filter(category=category, subcategory=subcategory)
    return render(request, 'product_list.html', {'category': category, 'subcategory': subcategory, 'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})


def display_two_products(request):
    categories = Category.objects.all()
    category_products = []
    for category in categories:
        products = Product.objects.filter(category=category)[:3]  # Retrieve only two products per category
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
