# Import all views from organized modules to maintain backward compatibility
# This allows existing code to continue using: from signup import views

from .auth import *
from .events import *  
from .user_profile import *
from .htmx import *
from .calendar_export import *
from .admin import *
