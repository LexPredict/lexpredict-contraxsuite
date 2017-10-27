from django.contrib import admin

# Project imports
from apps.employee.models import (Employee, Employer)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary')
    search_fields = ('name',)

class EmployerAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Employer, EmployerAdmin)
