from django.contrib import admin
from .models import Course, Category, Module, Content, Tier, WeUser, Quiz, Question, Option, QuizAttempt, UserBillingInfo

class BillingAdmin(admin.ModelAdmin):
    readonly_fields = ('transaction_id',)

admin.site.register(Course)
admin.site.register(Category)
admin.site.register(Module)
admin.site.register(Content)
admin.site.register(Tier)
admin.site.register(WeUser)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizAttempt)
admin.site.register(UserBillingInfo, BillingAdmin)


