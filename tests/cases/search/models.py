from django.db import models


class Office(models.Model):
    location = models.CharField(max_length=50)


class Title(models.Model):
    name = models.CharField(max_length=50)
    salary = models.IntegerField(null=True)
    boss = models.NullBooleanField(default=False)


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    title = models.ForeignKey(Title, null=True)
    office = models.ForeignKey(Office)
    is_manager = models.NullBooleanField(default=False)


class Meeting(models.Model):
    attendees = models.ManyToManyField(Employee)
    office = models.ForeignKey(Office)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)


class Project(models.Model):
    name = models.CharField(max_length=50)
    employees = models.ManyToManyField(Employee)
    manager = models.OneToOneField(Employee, related_name='managed_projects')
    due_date = models.DateField(null=True)
    budget = models.DecimalField(max_digits=7, decimal_places=2, null=True)
