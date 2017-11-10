from django.db import models
from apps.document.models import Document, TextUnit
from apps.extract.models import Usage



class Employer(models.Model):

    name = models.CharField(max_length=1024, db_index=True)

class EmployerUsage(Usage):

    employer= models.ForeignKey(Employer, db_index=True)

    class Meta:
        ordering=['-count']

class Employee(models.Model):

    document = models.ForeignKey(Document, db_index=True)
    name= models.CharField(max_length=1024, db_index=True)
    employer=models.ForeignKey(Employer, db_index=True, blank=True, null=True)
    annual_salary= models.FloatField(blank=True, null=True)
    salary_currency= models.CharField(max_length=10, blank=True, null=True)
    vacation_yearly= models.CharField(max_length=1024, db_index=True, null=True)
    effective_date= models.DateField(blank=True, null=True)
    governing_geo= models.CharField(max_length=1024, null=True, blank=True)
    has_noncompete= models.BooleanField(default=False)
    has_termination=models.BooleanField(default=False)
    has_benefits=models.BooleanField(default=False)


    class Meta:
        unique_together=(("name", "document"),)
        verbose_name_plural='Employees'
        ordering = ('name',)


    def __str__(self):
        return "Employee (" \
               "doc_id= {0}," \
               "name={0}," \
               "salary={2})" \
            .format(self.document.id, self.name, self.annual_salary)



class Provision(models.Model):

    text_unit= models.ForeignKey(TextUnit)
    similarity=models.DecimalField(max_digits=5, decimal_places=2)
    employee = models.ForeignKey(Employee)
    document=models.ForeignKey(Document)
    type= models.TextField(max_length=255) #noncompete, termination
