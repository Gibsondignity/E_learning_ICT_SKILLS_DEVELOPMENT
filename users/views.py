from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from learning.models import Student
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout



# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # or wherever you want to send them

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')




def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        full_name = request.POST['full_name']
        location = request.POST['location']
        secret_question = request.POST['secret_question']
        secret_answer = request.POST['secret_answer']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        user.first_name = full_name
        user.save()

        Student.objects.create(
            user=user,
            location=location,
            secret_question=secret_question,
            secret_answer=secret_answer
        )

        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')




def reset_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        secret_answer = request.POST['secret_answer']
        new_password = request.POST['new_password']

        try:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)

            if student.secret_answer.lower().strip() == secret_answer.lower().strip():
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successful. Please log in.")
                return redirect('login')
            else:
                messages.error(request, "Incorrect answer to secret question.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'reset_password.html')




def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')