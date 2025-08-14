from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    Student, Course, Lesson, QuizQuestion, StudentAnswer,
    Progress, LearningSession, Recommendation
)

# Customize the admin site
admin.site.site_header = "ICT SKILLS DEVELOPMENT"
admin.site.site_title = "ICT Skills Admin"
admin.site.index_title = "Admin Dashboard"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'interests')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'location')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('language', 'created_at')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'lesson', 'correct_option')
    search_fields = ('question_text', 'lesson__title')
    list_filter = ('lesson',)

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'selected_option', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('student__user__username', 'question__question_text')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'completed_at')
    search_fields = ('student__user__username', 'lesson__title')

@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'start_time', 'end_time', 'duration_minutes_display')
    list_filter = ('start_time', 'end_time')
    search_fields = ('student__user__username', 'lesson__title')

    def duration_minutes_display(self, obj):
        return round(obj.duration_minutes(), 2) if obj.duration_minutes() else 'Ongoing'
    duration_minutes_display.short_description = 'Duration (min)'

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
    search_fields = ('student__user__username', 'course__title')
    list_filter = ('created_at',)
