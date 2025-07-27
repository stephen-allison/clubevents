import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SignupApp.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SU_NAME')
email = os.environ.get('DJANGO_SU_EMAIL')
password = os.environ.get('DJANGO_SU_PWD')

if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created successfully!")
    else:
        print(f"Superuser '{username}' already exists")
else:
    print("Superuser environment variables not set")