from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


# models.py

import uuid

class UserBillingInfo(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    billing_address1 = models.CharField(max_length=200)
    billing_address2 = models.CharField(max_length=200)
    payment_info = models.CharField(max_length=100)
    country = CountryField(blank=True)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    card_holder_name = models.CharField(max_length=100, blank=True)
    card_number = models.CharField(max_length=16, blank=True)
    cvv = models.CharField(max_length=3, blank=True)
    expiry_date = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return self.customer_name

class WeUser(User):
    is_tutor = models.BooleanField(default=False)

    class Meta:
        verbose_name = "WeLearn User"
        verbose_name_plural = "WeLearn Users"


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
    tutor = models.ForeignKey(WeUser, on_delete=models.CASCADE)
    registered_users = models.ManyToManyField(WeUser, related_name='registered_courses')

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=250)
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    ordering = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['course', 'ordering']

    def __str__(self):
        return self.course.title + ' - ' + self.title


class Content(models.Model):
    file = models.FileField(upload_to="static/uploads")
    module = models.ForeignKey(Module, related_name="contents", on_delete=models.CASCADE)


class Quiz(models.Model):
    module = models.OneToOneField(Module, models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    grade_required = models.PositiveIntegerField(verbose_name="Percentage Required",
                                                 validators=[
                                                     MaxValueValidator(100),
                                                     MinValueValidator(1)
                                                 ]
                                                 )


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)


class QuizAttempt(models.Model):
    user = models.ForeignKey(WeUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    date_attempted = models.DateTimeField(auto_now=True)



