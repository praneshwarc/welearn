from django import forms
from .models import Course, WeUser, Option, Module
from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Option, UserBillingInfo


class CourseForm(forms.ModelForm):
    tier_name = forms.CharField(max_length=10)
    category_id = forms.CharField(max_length=25)

    class Meta:
        model = Course
        fields = ["title", "description", "tags", "hrs", "mins", "is_published", "tier_name", "category_id"]


class CourseEditForm(forms.ModelForm):
    tier_name = forms.CharField(max_length=10)
    category_id = forms.CharField(max_length=25)

    class Meta:
        model = Course
        fields = ["title", "description", "tags", "hrs", "mins", "is_published", "tier_name", "category_id"]


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
        questions = quiz.questions.all()
        for question in questions:
            options = Option.objects.filter(question=question)
            choices = [(option.id, option.text) for option in options]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
            )



class BillingInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BillingInfoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = 'text'
            if isinstance(field.widget, forms.EmailInput):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = 'text'
            if isinstance(field.widget, forms.NumberInput):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = 'text'
                if field_name=='amount':
                    field.widget.attrs['readonly'] = 'true'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'


    CURRENCY_CHOICES = [
        ('CAD', 'Canadian Dollar')
    ]

    payment_info = forms.ChoiceField(choices=[('credit', 'Credit Card'), ('debit', 'Debit Card'), ('paypal','PayPal')], label='Payment Method')
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    email = forms.EmailField(required=False, label = 'Email (Optional)')
    billing_address1 = forms.CharField(label='Address 1')
    billing_address2 = forms.CharField(required=False, label='Address 2 (Optional)')

    class Meta:
        model = UserBillingInfo
        fields = ['customer_name', 'email',  'billing_address1', 'billing_address2', 'country', 'state', 'postal_code', 'currency', 'payment_info', 'amount']


class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = 'text'


    expiry_date = forms.CharField(max_length=6, label="Expiry Date [MMYYYY]")
    class Meta:
        model = UserBillingInfo
        fields = ['card_holder_name', 'card_number', 'cvv', 'expiry_date']


class MailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MailForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = 'text'
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['style'] = 'height:100%'
                field.widget.attrs['rows'] = '3'
                field.widget.attrs['placeholder'] = 'text'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'

    #user_choices = [(user.id, user.first_name) for user in WeUser.objects.all()]
    user = forms.ModelChoiceField(queryset=WeUser.objects.all())
    message = forms.CharField(widget=forms.Textarea)


class ReplyForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)





