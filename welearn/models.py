from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
import uuid


class WeUser(User):
    is_tutor = models.BooleanField(default=False)
    tier = models.ForeignKey('Tier',null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "WeLearn User"
        verbose_name_plural = "WeLearn Users"


class Category(models.Model):
    label = models.CharField(max_length=25)
    tokens = models.CharField(max_length=200)

    def __str__(self):
        return self.label

    class Meta:
        ordering=["label"]
        verbose_name_plural = "Categories"


class Tier(models.Model):
    label = models.CharField(max_length=10)
    price = models.IntegerField(default=50)

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
    tutor = models.ForeignKey(WeUser, related_name="courses", on_delete=models.CASCADE)
    registered_users = models.ManyToManyField(WeUser, related_name='registered_courses', blank=True, null=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)

    def __str__(self):
        return self.course.title + ' - ' + self.title


class Content(models.Model):
    file = models.FileField(null=True,blank=True)
    youtube_video = models.URLField(null=True,blank=True)
    module = models.ForeignKey(Module, related_name="contents", on_delete=models.CASCADE)


class Quiz(models.Model):
    module = models.OneToOneField(Module, related_name="quiz", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    grade_required = models.PositiveIntegerField(verbose_name="Percentage Required",
                                                 validators=[
                                                     MaxValueValidator(100),
                                                     MinValueValidator(1)
                                                 ]
                                                 )


class Question(models.Model):
    quiz = models.ForeignKey(Quiz,related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()


class Option(models.Model):
    question = models.ForeignKey(Question,related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)


class QuizAttempt(models.Model):
    user = models.ForeignKey(WeUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    date_attempted = models.DateTimeField(auto_now=True)


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
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True)
    paypal_pid = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.customer_name


class Mail(models.Model):
    message = models.CharField(max_length=256)
    from_user = models.ForeignKey(WeUser, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(WeUser, on_delete=models.CASCADE, related_name='to_user')
    msg_time = models.DateTimeField()


# stripe models
class Price(models.Model):
    stripe_price_id = models.CharField(max_length=100)
    price = models.IntegerField(default=0)  # cents
    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)
