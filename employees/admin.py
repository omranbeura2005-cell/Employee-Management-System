from django.contrib import admin
from .models import Department , Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name','email','designation','salary','is_active','department','joining_date']

    list_filter = ['manager']
    search_fields = ['first_name','email'] 
    list_editable = ['salary']
    list_display_links = ['email']
    ordering = ["id"]

# Register your models here.
admin.site.register(Department)
admin.site.register(Employee , EmployeeAdmin)

