from django import forms
from .models import Course, WeUser, Option, Module
from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Option


class CourseForm(forms.ModelForm):
    tier_name = forms.CharField(max_length=10)
    category_name = forms.CharField(max_length=25)

    class Meta:
        model = Course
        fields = ["title", "description", "tags", "hrs", "mins", "is_published", "tier_name", "category_name"]


class CourseEditForm(forms.ModelForm):
    tier_name = forms.CharField(max_length=10)
    category_name = forms.CharField(max_length=25)

    class Meta:
        model = Course
        fields = ["title", "description", "tags", "hrs", "mins", "is_published", "tier_name", "category_name"]


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        exclude = ["course", ]


class ModuleEditForm(forms.ModelForm):
    class Meta:
        model = Module
        exclude = ["course", ]

    def __init__(self, *args, **kwargs):
        super(ModuleEditForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['description'].required = False


class SignUpForm(forms.ModelForm):
    class Meta:
        model = WeUser
        fields = ['username', 'first_name', 'last_name', 'password', 'is_tutor']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'is_tutor': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(max_length=50,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz')
        super(QuizForm, self).__init__(*args, **kwargs)
        questions = quiz.question_set.all()
        for question in questions:
            options = Option.objects.filter(question=question)
            choices = [(option.id, option.text) for option in options]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
            )


