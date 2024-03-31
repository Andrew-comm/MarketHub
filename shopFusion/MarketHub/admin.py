from django.contrib import admin
from .models import Category, SubCategory, Product 

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'subcategory')
    list_filter = ('category', 'subcategory')

    def get_queryset(self, request):
        # Exclude orphaned products (those with category or subcategory set to NULL)
        return super().get_queryset(request).exclude(category__isnull=True, subcategory__isnull=True)


admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product, ProductAdmin)

