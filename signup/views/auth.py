import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy, reverse

from ..forms import CustomUserCreationForm, EAURNLookupForm, EAEmailLookupForm
from ..models import PreRegistration, PendingVerification
from ..mail import send_email_verification


def ea_email_lookup_view(request):
    if request.method == 'POST':
        print('email form submitted')
        form = EAEmailLookupForm(request.POST)
        if form.is_valid():
            ea_email = form.cleaned_data['ea_email']

            try:
                prev_pending_verification = PendingVerification.objects.get(email=ea_email)
                prev_pending_verification.delete()
            except PendingVerification.DoesNotExist:
                pass
            finally:
                new_verification = PendingVerification.objects.create(email=ea_email)

            rel_uri = reverse('signup:email_verified',
                              kwargs={'token': str(new_verification.token),
                                      'ea_email': new_verification.email})
            link = request.build_absolute_uri(rel_uri)
            send_email_verification(new_verification.email, link)

            verify_context = {'email': ea_email, 'token': str(new_verification.token)}
            print(verify_context)
            return render(request, template_name='signup/verify_email.html', context=verify_context)
    else:
        form = EAEmailLookupForm()

    print('form errors: ', form.errors)
    return render(request, 'signup/eaemail_lookup.html', context={'form': form})



def verify_email_start(request, ea_email):
    try:
        pending_verification = PendingVerification.objects.get(email=ea_email)
        rel_uri = reverse('signup:email_verified',
                          kwargs={'token': str(pending_verification.uuid),
                                  'ea_email': pending_verification.email})
        link = request.build_absolute_uri(rel_uri)
        full_link = f'<a href="{link}">Click to verify your email</a>'
        send_email_verification(pending_verification.email, full_link)
        context = {
            'email': pending_verification.email,
            'token': str(pending_verification.uuid)
        }
        return render(request, 'signup/verify_email.html', context)
    except PendingVerification.DoesNotExist:
        pass
    return redirect('signup:activate_email')


def verify_email_finish(request, token, ea_email):
    try:
        pending_verification = PendingVerification.objects.get(email=ea_email)
        if not pending_verification.verify(token):
            return redirect('signup:activate_email')
        pending_verification.verified_time = datetime.datetime.now(datetime.timezone.utc)
        pending_verification.save()

        try:
            pre_reg = PreRegistration.objects.get(email=ea_email)
            print(f'found pre registration  {pre_reg}')
            pre_reg.email_verified = True
            pre_reg.save()
        except PreRegistration.DoesNotExist:
            print('Pre-registration not found.')
            redirect('signup:activate_email')

        return render(request, 'signup/email_verified.html')
    except PendingVerification.DoesNotExist:
        return redirect('signup:activate_email')

def check_email_verification(request, email):
    verified = PendingVerification.objects.filter(email=email, verified_time__isnull=False).exists()
    if verified:
        template = 'signup/email_verified_continue.html'
    else:
        template = 'signup/email_verification_await.html'
    context = {'email': email}

    return render(request, template, context)

def register_with_preregistration_view_email(request, token, ea_email):
    try:
        preregistration = PreRegistration.objects.get(email=ea_email)
        if not preregistration.email_verified:
            print('pre reg email not verified')
            return redirect('signup:activate_email')
    except PreRegistration.DoesNotExist:
        messages.error(request, 'Invalid email address or pre-registration not found.')
        print('no email found')
        return redirect('signup:activate_email')

    # Check if user already exists
    User = get_user_model()
    if User.objects.filter(email=ea_email).exists():
        messages.error(request, 'A user account already exists with this email.')
        return redirect('signup:login')

    # Store token and email in session for form submission
    request.session['registration_token'] = token
    request.session['registration_email'] = ea_email

    form = CustomUserCreationForm(preregistration=preregistration)
    return render(request, 'signup/register_with_preregistration.html', {
        'form': form,
        'preregistration': preregistration
    })


def register_form_submit(request):
    """Handle POST submission of registration form"""
    if request.method != 'POST':
        return redirect('signup:activate_email')
    
    # Get token and email from session
    token = request.session.get('registration_token')
    ea_email = request.session.get('registration_email')
    
    if not token or not ea_email:
        messages.error(request, 'Registration session expired. Please start again.')
        return redirect('signup:activate_email')

    try:
        preregistration = PreRegistration.objects.get(email=ea_email)
        if not preregistration.email_verified:
            return redirect('signup:activate_email')
    except PreRegistration.DoesNotExist:
        messages.error(request, 'Invalid registration data.')
        return redirect('signup:activate_email')

    # Check if user already exists (double-check)
    User = get_user_model()
    if User.objects.filter(email=ea_email).exists():
        messages.error(request, 'A user account already exists with this email.')
        return redirect('signup:login')

    form = CustomUserCreationForm(preregistration=preregistration, data=request.POST)
    if form.is_valid():
        user = form.save(commit=True)
        print(f'created user {user}')

        preregistration.activated = True
        preregistration.save()

        # Clear session data
        request.session.pop('registration_token', None)
        request.session.pop('registration_email', None)

        # Log the user in
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('signup:event_list_signups')
    else:
        # If form is invalid, redisplay with errors
        return render(request, 'signup/register_with_preregistration.html', {
            'form': form,
            'preregistration': preregistration
        })

class CustomLoginView(LoginView):
    template_name = 'signup/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('signup:event_list_signups')