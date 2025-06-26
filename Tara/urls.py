from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from rest_framework import permissions
from Tara.utils import *  # Custom utility imports
from django.conf import settings
from django.conf.urls.static import static



# Initial URL patterns
urlpatterns = [
    # Include user management URLs
    # path('user_management/', include('user_management.urls')),
    # Include Invoicing URLs
    path('invoicing/', include('invoicing.urls')),
    # Include Invoicing URLs
    path('payroll/', include('payroll.urls')),

    path('user_management/', include('usermanagement.urls')),

    path('companyincorporation/',include('company_incorporation.urls')),

    path('gst/', include('gst.urls')),

    path('labourlicense/', include('labour_license.urls')),

    path('servicetasks/', include('servicetasks.urls')),

    path('income_tax_returns/', include('income_tax_returns.urls')),

    path('msme/', include('msme_registration.urls')),

    path('docwallet/', include('docwallet.urls')),

    path('tradelicense/', include('trade_license.urls')),
    # Token authentication URL
    path('token_auth/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


