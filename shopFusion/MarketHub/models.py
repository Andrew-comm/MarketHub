from django.db import models




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



