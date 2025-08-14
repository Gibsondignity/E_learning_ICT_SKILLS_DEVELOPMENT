# elearning/ai.py

from .models import Course, Recommendation

def recommend_courses_for_student(student):
    if not student.interests:
        return

    interests = student.interests.lower().split(",")
    matched_courses = Course.objects.filter(
        title__icontains=interests[0]
    )[:3]

    for course in matched_courses:
        Recommendation.objects.get_or_create(
            student=student,
            course=course,
            defaults={'reason': f"Matches your interest in {interests[0]}"}
        )

