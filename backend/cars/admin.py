from django.contrib import admin
from .models import Car

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price', 'is_available', 'owner', 'created_at')
    list_filter = ('is_available', 'make', 'year', 'owner')
    search_fields = ('make', 'model', 'description')
    date_hierarchy = 'created_at'
