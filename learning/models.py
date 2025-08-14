# elearning/models.py

from django.contrib.auth.models import User
from django.db import models

# 1. Student Profile (linked to Django User)
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True)
    location = models.CharField(max_length=100, blank=True)
    interests = models.TextField(blank=True)
    secret_question = models.CharField(max_length=255, help_text="E.g., What is your favorite color?", null=True, blank=True)
    secret_answer = models.CharField(max_length=100, help_text="Answer to your secret question", null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    language = models.CharField(max_length=50, default='English')
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class QuizQuestion(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='quiz_questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    def __str__(self):
        return f"{self.lesson.title} - {self.question_text[:30]}"

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')])
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.question} - {self.selected_option} - {'Correct' if self.is_correct else 'Incorrect'}"

class Progress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student} - {self.lesson} - {'Done' if self.completed else 'Pending'}"

class LearningSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def duration_minutes(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return None

class Recommendation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    reason = models.TextField(help_text="Why this was recommended")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.course} recommended to {self.student}"
