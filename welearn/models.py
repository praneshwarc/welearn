from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User


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
    tutor = models.ForeignKey(WeUser, related_name="courses", on_delete=models.CASCADE)
    registered_users = models.ManyToManyField(WeUser, related_name='registered_courses')

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
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
    date_attempted = models.DateTimeField(auto_now=True)



