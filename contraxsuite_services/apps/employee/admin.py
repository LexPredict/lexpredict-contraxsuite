from django.contrib import admin

# Project imports
from apps.employee.models import (Employee, Employer,Provision)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'annual_salary')
    search_fields = ('name',)

class EmployerAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ProvisionAdmin(admin.ModelAdmin):
    list_display =('text_unit', 'similarity', 'type')

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(Provision, ProvisionAdmin)
