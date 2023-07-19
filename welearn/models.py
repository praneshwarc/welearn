from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    label = models.CharField(max_length=25)
    tokens = models.CharField(max_length=200)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "Categories"


class Tier(models.Model):
    label = models.CharField(max_length=10)

    def __str__(self):
        return self.label


class Course(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.CharField(max_length=200)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    hrs = models.PositiveIntegerField()
    mins = models.PositiveIntegerField()
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=250)
    course = models.ForeignKey(Course,related_name='modules', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Content(models.Model):
    file = models.FileField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE)


class Student(User):
    registered_courses = models.ManyToManyField(Course)

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Tutor(User):
    owned_courses = models.ManyToManyField(Course)

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutors"
