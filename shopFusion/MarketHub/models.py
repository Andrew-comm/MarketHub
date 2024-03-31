from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin   


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self.create_user(email, password, **extra_fields)

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     groups = models.ManyToManyField(
#         'auth.Group',
#         verbose_name='groups',
#         blank=True,
#         related_name='customuser_set',  # Unique related name for groups
#         related_query_name='user',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         verbose_name='user permissions',
#         blank=True,
#         related_name='customuser_set',  # Unique related name for user permissions
#         related_query_name='user',
#     )

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
    

#     REQUIRED_FIELDS = ['first_name', 'last_name']

#     def __str__(self):
#         return self.email

class Category(models.Model):
    """
    Model for product categories and subcategories.
    """
    name = models.CharField(max_length=100, unique=True)  # Ensures unique category names
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        """
        String representation of the category, including its parent category if applicable.
        """
        full_path = [self.name]
        parent = self.parent
        while parent:
            full_path.append(parent.name)
            parent = parent.parent
        return ' -> '.join(full_path[::-1])  # Reverse list to show hierarchy

class SubCategory(models.Model):
    """
    Model for product subcategories that belong to a specific category.
    """
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # Links each subcategory to a parent category

    def __str__(self):
        """
        String representation of the subcategory, including its name and category.
        """
        return f"{self.name} ({self.category.name if self.category else 'No category'})"

class Product(models.Model):
    """
    Model for individual products with category and subcategory association.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True)  # Optional product image
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # Set category to NULL if related category is deleted
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)  # Set subcategory to NULL if related subcategory is deleted
    cart_quantity = models.PositiveIntegerField(default=0)  # New field to store cart quantity

    def __str__(self):
        """
        String representation of the product with name, price, and category.
        """
        return f"{self.name} - ${self.price} ({self.category.name if self.category else 'No category'})"


