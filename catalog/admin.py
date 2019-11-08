from django.contrib import admin
from .models import Category, Product, Substitute
from django.utils.text import Truncator


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_filter = ('id', 'name',)
    ordering = ('id', )
    search_fields = ('id', 'name')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'preview_product', 'nutri_score', 'picture', 'category')
    list_filter = ('nutri_score', 'category')
    ordering = ('id', )
    search_fields = ('id', 'name', 'nutri_score', 'category')

    def preview_product(self, product):
        return Truncator(product.name).chars(20, truncate='...')


class SubstituteAdmin(admin.ModelAdmin):
    list_display = ('id', 'preview_substitute', 'nutri_score', 'preview_url', 'nutrition', 'picture')
    list_filter = ('nutri_score',)
    ordering = ('id', )
    search_fields = ('id', 'name', 'nutri_score')

    def preview_url(self, substitute):
        return Truncator(substitute.url).chars(40, truncate='...')

    def preview_substitute(self, substitute):
        return Truncator(substitute.name).chars(20, truncate='...')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Substitute, SubstituteAdmin)
