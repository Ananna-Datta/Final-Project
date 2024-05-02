from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth.forms import  AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login , update_session_auth_hash, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# Create your views here.
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives



# def add_author(request):
#     if request.method == 'POST':
#         author_form = forms.AuthorForm(request.POST)
#         if author_form.is_valid():
#             author_form.save()
#             return redirect('add_author')
    
#     else:
#         author_form = forms.AuthorForm()
#     return render(request, 'add_author.html', {'form' : author_form})
def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "Your account has been activated. You can now log in.")
        return redirect('user_login')
    else:
        messages.error(request, "Invalid activation link.")
        return redirect('register')
    
    
def signup(request):
    if not request.user.is_authenticated:
        form = forms.RegisterForm()
        if request.method == 'POST':
            form = forms.RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.is_active = False  # The user is inactive until activation
                user.save()

                # Generate activation link with the correct domain
                current_site = get_current_site(request)
                # Generate activation link
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # confirm_link = f'http://127.0.0.1:8000/accounts/activate/{uid}/{token}'
                confirm_link = f'http://{current_site.domain}/author/activate/{uid}/{token}'

                # Send activation email
                email_subject = "Confirm your email"
                email_body = render_to_string(
                    'email_confirmation.html',
                    {'user': user, 'confirm_link': confirm_link}
                )
                email = EmailMultiAlternatives(
                    subject=email_subject, body=email_body, to=[user.email]
                )
                email.attach_alternative(email_body, 'text/html')
                email.send()

                messages.success(
                    request, 'Check your email and click on the link to activate your account.')
                # return redirect('login')
                return redirect('register')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = forms.RegisterForm()

        return render(request, 'form.html', {'form': form, 'title': 'Sign Up', 'button_text': 'Sign Up', 'button_class': 'btn-success'})
    else:
        return redirect('homepage')
    
    
def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)

                    # messages.success(request, 'Logged In Successfully')
                    messages.info(
                        request, f"You are now logged in as {username}")

                    # Redirect to the appropriate page after login
                    return redirect('profile')
                else:
                    messages.error(request, 'Invalid username or password')

        else:
            form = AuthenticationForm()

        return render(request, 'form.html', {'form': form, 'title': 'Login', 'button_text': 'Login', 'button_class': 'btn-primary'})
    else:
        return redirect('homepage')


# class UserLoginView(LoginView):
    # template_name = 'register.html'
    # # success_url = reverse_lazy('profile')
    # def get_success_url(self):
    #     return reverse_lazy('profile')
    # def form_valid(self, form):
    #     messages.success(self.request, 'Logged in Successful')
    #     return super().form_valid(form)
    
    # def form_invalid(self, form):
    #     messages.success(self.request, 'Logged in information incorrect')
    #     return super().form_invalid(form)
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['type'] = 'Login'
    #     return context
  

@login_required
def profile(request):
    data = Post.objects.filter(author = request.user)
    return render(request, 'profile.html', {'data' : data})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = forms.ChangeUserForm(request.POST, instance = request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('profile')
    
    else:
        profile_form = forms.ChangeUserForm(instance = request.user)
    return render(request, 'update_profile.html', {'form' : profile_form})


def pass_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password Updated Successfully')
            update_session_auth_hash(request, form.user)
            return redirect('profile')
    
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'pass_change.html', {'form' : form})


def user_logout(request):
    logout(request)
    return redirect('homepage')