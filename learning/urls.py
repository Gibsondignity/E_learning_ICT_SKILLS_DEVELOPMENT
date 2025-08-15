from django.urls import path
from . import views
urlpatterns = [
    path('welcome-to-your-ai-dashboard-for-ict-development/', views.dashboard_view, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('progress_leaderboard_view/', views.progress_leaderboard_view, name='progress'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('dashboard/quizzes/', views.quizzes_view, name='quizzes'),
    path('dashboard/quiz/<int:lesson_id>/start/', views.start_quiz_view, name='start_quiz'),
    path('dashboard/quiz/<int:lesson_id>/result/', views.quiz_result_view, name='quiz_result'),
    path('courses/<int:course_id>/enroll/', views.enroll_in_course, name='enroll_course'),

    path('ai-recommendations/', views.ai_recommendations_view, name='ai_recommendations'),
]