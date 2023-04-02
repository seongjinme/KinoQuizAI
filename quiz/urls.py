from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('quiz/', views.quiz_view, name='quiz'),

    path('api/quiz/create', views.get_quiz, name='get_quiz'),
    path('api/quiz/<str:quiz_id>/result', views.get_result, name='get_result'),
]
