from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg, Sum
from .models import Course, Lesson, Progress, Recommendation, StudentAnswer, QuizQuestion, LearningSession, Student
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .utils import recommend_courses_for_student
from django.contrib import messages
from django.db import transaction



@login_required
def dashboard_view(request):
    student = request.user
    student_profile = getattr(student, 'student_profile', None)

    # enrolled_courses = Course.objects.filter(progress__student=student).distinct()[:3]
    total_lessons = Lesson.objects.count()
    lessons_completed = Progress.objects.filter(student=student_profile, completed=True).count()
    lessons_percent = int((lessons_completed / total_lessons) * 100) if total_lessons else 0

    recommendations = Recommendation.objects.filter(student=student_profile)[:3]
    recent_activities = [
        "Completed Lesson 2: Introduction to Computers",
        "Scored 80% in Quiz: Digital Literacy",
        "Started Course: Basic Networking"
    ]

    return render(request, 'main/dashboard.html', {
        'student': student,
        # 'enrolled_courses': enrolled_courses,
        'lessons_completed': lessons_completed,
        'total_lessons': total_lessons,
        'lessons_percent': lessons_percent,
        'recommendations': recommendations,
        'recent_activities': recent_activities,
        'now': timezone.now(),
    })




@login_required
def course_list(request):
    courses = Course.objects.all()
    
    return render(request, 'main/course_list.html', {'courses': courses, 'now': timezone.now(),})



@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()

    # Try to get the Student profile using the correct related_name
    student = getattr(request.user, 'student_profile', None)

    # Initialize variables for both cases (with and without student)
    completed_lessons = 0
    total_lessons = lessons.count()
    progress_percent = 0
    badge = None
    next_lesson = None
    completed_ids = []
    is_enrolled = False

    # Check enrollment status regardless of student profile existence
    from .models import CourseEnrollment
    if student:
        is_enrolled = CourseEnrollment.objects.filter(student=student, course=course).exists()
        
        # Calculate progress for enrolled students
        completed_lessons = Progress.objects.filter(
            student=student,
            lesson__course=course,
            completed=True
        ).count()

        progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        completed_ids = Progress.objects.filter(
            student=student,
            lesson__course=course,
            completed=True
        ).values_list('lesson_id', flat=True)

        next_lesson = lessons.exclude(id__in=completed_ids).order_by('order').first()

        if completed_lessons == 1:
            badge = "Starter Learner"
        elif completed_lessons == total_lessons:
            badge = "Course Master"
        else:
            badge = None

    return render(request, 'main/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'progress_percent': progress_percent,
        'badge': badge,
        'next_lesson': next_lesson,
        'completed_ids': list(completed_ids) if completed_ids else [],
        'now': timezone.now(),
        'student': student,
        'is_enrolled': is_enrolled,
    })



@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    # Get the Student instance linked to the current user
    try:
        student = request.user.student_profile  # because of related_name='student_profile'
    except Student.DoesNotExist:
        # Handle case where Student profile doesn't exist
        # Optionally: create it, or redirect to profile setup
        return redirect('create_student_profile')  # or some other page

    # Track progress using the Student instance
    progress, created = Progress.objects.get_or_create(
        student=student,
        lesson=lesson
    )

    if request.method == 'POST' and 'complete' in request.POST:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return redirect('course_detail', course.id)

    return render(request, 'main/lesson_detail.html', {
        'lesson': lesson,
        'course': course,
        'progress': progress,
        'now': timezone.now(),
    })



@login_required
def quizzes_view(request):
    student = request.user.student_profile

    # Lessons the student has completed
    completed_lessons = Progress.objects.filter(student=student, completed=True).select_related('lesson')
    
    # Prepare quiz data for each lesson
    quiz_data = []
    for progress in completed_lessons:
        lesson = progress.lesson
        questions = lesson.quiz_questions.all()
        if not questions.exists():
            continue

        total_questions = questions.count()
        correct_answers = StudentAnswer.objects.filter(
            student=student,
            question__lesson=lesson,
            is_correct=True
        ).count()

        total_attempted = StudentAnswer.objects.filter(
            student=student,
            question__lesson=lesson
        ).count()

        score_percent = int((correct_answers / total_questions) * 100) if total_questions else 0

        quiz_data.append({
            'lesson': lesson,
            'total_questions': total_questions,
            'total_attempted': total_attempted,
            'correct_answers': correct_answers,
            'score_percent': score_percent,
            'now': timezone.now(),
        })

    return render(request, 'main/dashboard_quizzes.html', {
        'quiz_data': quiz_data
    })





@login_required
def start_quiz_view(request, lesson_id):
    student = request.user.student_profile
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = QuizQuestion.objects.filter(lesson=lesson)

    if request.method == 'POST':
        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected:
                is_correct = selected == question.correct_option
                StudentAnswer.objects.update_or_create(
                    student=student,
                    question=question,
                    defaults={
                        'selected_option': selected,
                        'is_correct': is_correct,
                        'answered_at': timezone.now()
                    }
                )
        return redirect('quiz_result', lesson_id=lesson.id)

    return render(request, 'main//start_quiz.html', {
        'lesson': lesson,
        'questions': questions,
    })



@login_required
def quiz_result_view(request, lesson_id):
    student = request.user.student_profile
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = QuizQuestion.objects.filter(lesson=lesson)
    total = questions.count()
    correct = StudentAnswer.objects.filter(student=student, question__in=questions, is_correct=True).count()

    score_percent = int((correct / total) * 100) if total else 0

    # Automatically mark lesson as completed after quiz submission
    progress, created = Progress.objects.get_or_create(
        student=student,
        lesson=lesson,
        defaults={
            'completed': True,
            'completed_at': timezone.now()
        }
    )
    
    # If progress already existed but wasn't completed, mark it as completed
    if not created and not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

    return render(request, 'main//quiz_result.html', {
        'lesson': lesson,
        'total': total,
        'correct': correct,
        'score_percent': score_percent
    })



@login_required
def progress_leaderboard_view(request):
    student = request.user.student_profile

    # Total progress
    total_lessons = Lesson.objects.count()
    lessons_completed = Progress.objects.filter(student=student, completed=True).count()
    progress_percent = int((lessons_completed / total_lessons) * 100) if total_lessons else 0

    # Time spent
    sessions = LearningSession.objects.filter(student=student, end_time__isnull=False)
    total_duration = timedelta()
    for session in sessions:
        if session.start_time and session.end_time:
            total_duration += session.end_time - session.start_time

    # Quiz stats
    total_answers = StudentAnswer.objects.filter(student=student).count()
    correct_answers = StudentAnswer.objects.filter(student=student, is_correct=True).count()
    quiz_accuracy = int((correct_answers / total_answers) * 100) if total_answers else 0

    # Leaderboard by lessons completed
    leaderboard = (
        Progress.objects.filter(completed=True)
        .values('student__user__username')
        .annotate(completed_lessons=Count('lesson'))
        .order_by('-completed_lessons')[:5]
    )

    return render(request, 'main/progress_leaderboard.html', {
        'progress_percent': progress_percent,
        'lessons_completed': lessons_completed,
        'total_lessons': total_lessons,
        'quiz_accuracy': quiz_accuracy,
        'leaderboard': leaderboard,
        'student': student,
        'now': timezone.now(),
        'total_time_spent': total_duration,
    })




@login_required
def enroll_in_course(request, course_id):
    from .models import CourseEnrollment
    
    course = get_object_or_404(Course, id=course_id)

    # Get or create the student profile
    student = getattr(request.user, 'student_profile', None)
    if not student:
        # Create a student profile automatically
        student = Student.objects.create(user=request.user)
        messages.info(request, "Student profile created automatically.")

    # Check if already enrolled (via CourseEnrollment model)
    if CourseEnrollment.objects.filter(student=student, course=course).exists():
        messages.info(request, "You're already enrolled in this course.")
    else:
        # Enroll student in course
        with transaction.atomic():
            CourseEnrollment.objects.create(
                student=student,
                course=course
            )
            
            # Also create progress for the first lesson (not marked as complete)
            first_lesson = course.lessons.order_by('order', 'id').first()
            if first_lesson:
                Progress.objects.get_or_create(
                    student=student,
                    lesson=first_lesson,
                    defaults={
                        'completed': False,
                        'completed_at': None
                    }
                )
            
        messages.success(request, f"You've successfully enrolled in '{course.title}'! 🎉")

    return redirect('course_detail', course_id=course.id)



@login_required
def ai_recommendations_view(request):
    student = request.user.student_profile
    recommendations = Recommendation.objects.filter(student=student)

    if not recommendations.exists():
        recommend_courses_for_student(student)
        recommendations = Recommendation.objects.filter(student=student)

    return render(request, 'main/ai_recommendations.html', {
        'student': student,
        'recommendations': recommendations,
    })