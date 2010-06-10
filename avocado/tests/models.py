from django.db import models

__all__ = ('Root', 'Parent1', 'Parent2', 'Child1', 'Child2', 'Child3', 'Foo',
    'Bar', 'Baz', 'Bear')

class Root(models.Model):
    name = models.CharField(max_length=100)


class Parent1(models.Model):
    parent = models.ForeignKey(Root, related_name='crazy_parent')
    name = models.CharField(max_length=100)


class Parent2(models.Model):
    parent = models.ForeignKey(Root, related_name='wacky_parent')
    name = models.CharField(max_length=100)


class Child1(models.Model):
    parent = models.ForeignKey(Parent1)
    name = models.CharField(max_length=100)


class Child2(models.Model):
    parent = models.OneToOneField(Parent2)
    bar = models.ForeignKey('Bar', related_name='cool_child')
    name = models.CharField(max_length=100)


class Child3(models.Model):
    parent = models.ForeignKey(Root)
    name = models.CharField(max_length=100)


class Foo(models.Model):
    parent = models.ForeignKey(Child3, related_name='fooey')
    name = models.CharField(max_length=100)


class Bar(models.Model):
    parent = models.ForeignKey(Foo)
    root = models.ForeignKey(Root, related_name='barman')
    name = models.CharField(max_length=100)


class Baz(models.Model):
    parent = models.ForeignKey(Bar)
    name = models.CharField(max_length=100)


class Bear(models.Model):
    bazes = models.ManyToManyField(Baz, related_name='many_bears')