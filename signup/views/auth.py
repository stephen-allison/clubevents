import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy, reverse

from ..forms import CustomUserCreationForm, EAURNLookupForm, EAEmailLookupForm
from ..models import PreRegistration, PendingVerification
from ..mail import send_email_verification


def ea_urn_lookup_view(request):
    if request.method == 'POST':
        form = EAURNLookupForm(request.POST)
        if form.is_valid():
            ea_urn = form.cleaned_data['ea_urn']
            # Redirect to registration form with EA URN in URL
            return redirect('signup:register_with_preregistration', ea_urn=ea_urn)
    else:
        form = EAURNLookupForm()

    return render(request, 'signup/eaurn_lookup.html', {'form': form})


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
            full_link = f'<a href="{link}">Click to verify your email</a>'
            send_email_verification(new_verification.email, full_link)

            verify_context = {'email': ea_email, 'token': str(new_verification.token)}
            print(verify_context)
            return render(request, template_name='signup/verify_email.html', context=verify_context)
    else:
        form = EAEmailLookupForm()

    print('form errors: ', form.errors)
    return render(request, 'signup/eaemail_lookup.html', context={'form': form})

def register_with_preregistration_view(request, ea_urn):
    # Get the preregistration data
    try:
        preregistration = PreRegistration.objects.get(ea_urn=ea_urn)
    except PreRegistration.DoesNotExist:
        messages.error(request, 'Invalid EA URN or pre-registration not found.')
        return redirect('signup:activate')

    # Check if user already exists
    User = get_user_model()
    if User.objects.filter(ea_urn=ea_urn).exists():
        messages.error(request, 'A user account already exists with this EA URN.')
        return redirect('signup:login')

    if request.method == 'POST':
        form = CustomUserCreationForm(preregistration=preregistration, data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.ea_urn = ea_urn  # Set the EA URN from the lookup
            user.save()

            preregistration.activated = True
            preregistration.save()

            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('signup:event_list_signups')
    else:
        form = CustomUserCreationForm(preregistration=preregistration)

    return render(request, 'signup/register_with_preregistration.html', {
        'form': form,
        'preregistration': preregistration
    })

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
        return render(request, 'signup/email_verified.html')
    except PendingVerification.DoesNotExist:
        return redirect('signup:activate_email')



def register_with_preregistration_view_email(request, token, ea_email):
    try:
        pending_verification = PendingVerification.objects.get(email=ea_email)
        if token != str(pending_verification.uuid):
            return redirect('signup:activate_email')
    except PendingVerification.DoesNotExist:
        return redirect('signup:activate_email')
    # Get the preregistration data
    print(f'email verified {pending_verification.email}')
    try:
        preregistration = PreRegistration.objects.get(email=ea_email)
    except PreRegistration.DoesNotExist:
        messages.error(request, 'Invalid email address or pre-registration not found.')
        print('no email found')
        return redirect('signup:activate_email')

    # Check if user already exists
    User = get_user_model()
    if User.objects.filter(email=ea_email).exists():
        messages.error(request, 'A user account already exists with this EA URN.')
        return redirect('signup:login')

    if request.method == 'POST':
        form = CustomUserCreationForm(preregistration=preregistration, data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.ea_urn = ea_email  # Set the EA URN from the lookup
            user.save()

            preregistration.activated = True
            preregistration.save()

            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('signup:event_list_signups')
    else:
        form = CustomUserCreationForm(preregistration=preregistration)

    return render(request, 'signup/register_with_preregistration.html', {
        'form': form,
        'preregistration': preregistration
    })

class CustomLoginView(LoginView):
    template_name = 'signup/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('signup:event_list_signups')