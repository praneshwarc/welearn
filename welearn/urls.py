from django.urls import path
from . import views
from .views import AddContent, ContentView, DeleteQuiz, EnrollCourse, CourseDashboard, CourseProgress

app_name = 'welearn'
urlpatterns = [
    path('', views.student_home, name='student_home'),
    path('home/', views.student_home, name='student_home'),
    path('courses/<int:course_id>/', views.course, name='course'),
    path('tutor/', views.tutor_home, name='tutor_home'),
    path('tutor/home/', views.tutor_home, name='tutor_home'),
    path('tutor/course/<int:course_id>/', views.tutor_course_id, name='tutor_course_id'),
    path('tutor/course/<int:course_id>/modules/', views.tutor_modules, name='tutor_modules'),
    path('tutor/module/<int:module_id>/', views.tutor_module_id, name="tutor_module_id"),
    path('login/', views.login_view, name="login"),
    path('signup/', views.sign_up, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('quiz/<int:module_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz_result/<int:module_id>/', views.quiz_result, name='quiz_result'),
    path('profile/', views.profile, name='profile'),
    path('tutor/module/<int:module_id>/content', AddContent.as_view(), name="add_content"),
    path('tutor/content/<int:content_id>/', ContentView.as_view(), name="delete_content"),
    path('tutor/module/<int:module_id>/create_quiz/', views.create_quiz, name='create-quiz'),
    path('tutor/quiz/<int:quiz_id>/', DeleteQuiz.as_view(), name = 'delete_quiz'),
    path('search',views.search,name='search'),
    path("course/<int:course_id>/enroll/", EnrollCourse.as_view(), name="enroll"),
    path("tutor/course/<int:course_id>/dashboard/<int:student_id>/", CourseProgress.as_view(), name="student_progress"),
    path("tutor/course/<int:course_id>/dashboard/", CourseDashboard.as_view(), name="course_dashboard"),
    #path("cert/", views.get_cert_page),
    path('billing/', views.billing_page, name='billing_page'),
    path('payment/', views.payment_page, name='payment_page'),
    path('payment/success/', views.success_page, name='success_page'),
    path('payment/fail/', views.payment_fail_page, name='payment_fail_page'),
    path('mail/', views.mail, name="mail"),
    path('my_messages/', views.my_messages, name="my_messages"),
    path('cert/<int:course_id>/', views.download_certificate, name="get_cert"),
    path('create-checkout-session/<int:pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('stripel/', ProductLandingPageView.as_view() )
]
