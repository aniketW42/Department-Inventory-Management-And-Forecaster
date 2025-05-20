from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User, Group
from .utils import is_hod, is_clerk, is_faculty

@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Invalid Credentials')
    return render(request, 'user/login.html')


@login_required
@user_passes_test(is_hod)
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        group_name = request.POST.get('group')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
            return redirect('create_user')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address provided.")
            return redirect('create_user')

        try:
            # Create user
            user = User.objects.create_user(username=username, password=password, email=email)

            # Assign group
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                user.delete()  # rollback
                messages.error(request, f"Group '{group_name}' does not exist.")
                return redirect('create_user')

            # Send welcome email
            subject = "Your Inventory System Account"
            message = render_to_string('emails/account_created_email.txt', {
                'username': username,
                'password': password,
            })

            send_mail(
                subject,
                message,
                'aniketwakte42@gmail.com',
                [email],
                fail_silently=False
            )

            messages.success(request, f"User {username} created successfully and notified by email.")
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect('create_user')

    return render(request, 'user/create_user.html')
