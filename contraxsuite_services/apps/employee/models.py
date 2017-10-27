from django.db import models
from apps.document.models import Document



class Employer(models.Model):

    name = models.CharField(max_length=1024, db_index=True)

    def __str__(self):
        return "Employer: %s" % self.name


class Employee(models.Model):

    document = models.ForeignKey(Document, db_index=True)
    name= models.CharField(max_length=1024, db_index=True)
    employer=models.ForeignKey(Employer, db_index=True)
    title= models.CharField(max_length=1024, db_index=True)#TODO- determine if you can actually get this or delete this from model
    salary= models.FloatField()
    effective_date= models.DateField(null=True)


    class Meta:
        unique_together=(("name", "document"),)
        verbose_name_plural='Employees'


    def __str__(self):
        return "Employee (" \
               "doc_id= {0}," \
               "name={0}," \
               "title={1}," \
               "salary={2})" \
            .format(self.document.id, self.name, self.title, self.salary)



class Noncompete_Provision:

    text_unit= models.TextField(max_length=16384)
    similarity=models.DecimalField(max_digits=5, decimal_places=2)
    employee = models.ForeignKey(Employee)
    document=models.ForeignKey(Document)
