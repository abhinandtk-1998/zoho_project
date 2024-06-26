#zoho Final
from django.urls import path,re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

urlpatterns = [
    # -------------------------------Company section--------------------------------
    path('Company/Dashboard',views.company_dashboard,name='company_dashboard'),
    path('Company/Staff-Request',views.company_staff_request,name='company_staff_request'),
    path('Company/Staff-Request/Accept/<int:pk>',views.staff_request_accept,name='staff_request_accept'),
    path('Company/Staff-Request/Reject/<int:pk>',views.staff_request_reject,name='staff_request_reject'),
    path('Company/All-Staffs',views.company_all_staff,name='company_all_staff'),
    path('Company/Staff-Approval/Cancel/<int:pk>',views.staff_approval_cancel,name='staff_approval_cancel'),
    path('Company/Profile',views.company_profile,name='company_profile'),
    path('Company/Profile-Editpage',views.company_profile_editpage,name='company_profile_editpage'),
    path('Company/Profile/Edit/Basicdetails',views.company_profile_basicdetails_edit,name='company_profile_basicdetails_edit'),
    path('Company/Password_Change',views.company_password_change,name='company_password_change'),
    path('Company/Profile/Edit/Companydetails',views.company_profile_companydetails_edit,name='company_profile_companydetails_edit'),
    path('Company/Module-Editpage',views.company_module_editpage,name='company_module_editpage'),
    path('Company/Module-Edit',views.company_module_edit,name='company_module_edit'),
    path('Company/Renew/Payment_terms',views.company_renew_terms,name='company_renew_terms'),
    path('Company/Notifications',views.company_notifications,name='company_notifications'),
    path('company/messages/read/<int:pk>',views.company_message_read,name='company_message_read'),
    path('Company/Payment_History',views.company_payment_history,name='company_payment_history'),
    path('Company/Trial/Review',views.company_trial_feedback,name='company_trial_feedback'),
    path('Company/Profile/Edit/gsttype',views.company_gsttype_change,name='company_gsttype_change'),

    path('Company/Payroll/Holiday',views.company_holiday,name='company_holiday'),
    path('Company/Payroll/Holiday/New',views.company_holiday_new,name='company_holiday_new'),
    path('Company/Payroll/Holiday/import_sample_download',views.company_holiday_import_sample_download,name='company_holiday_import_sample_download'),
    path('Company/Payroll/Holiday/Import_operation',views.company_holiday_import_operation,name='company_holiday_import_operation'),
    path('Company/Payroll/Holiday/New_add',views.company_holiday_new_add,name='company_holiday_new_add'),
    path('Company/Payroll/Holiday/Overview',views.company_holiday_overview,name='company_holiday_overview'),
    path('Company/Payroll/Holiday/Overview_delete/<int:pk>',views.company_holiday_overview_delete,name='company_holiday_overview_delete'),
    path('Company/Payroll/Holiday/Overview_edit/<int:pk>',views.company_holiday_overview_edit,name='company_holiday_overview_edit'),
    path('Company/Payroll/Holiday/Overview_edit_op/<int:pk>',views.company_holiday_overview_edit_op,name='company_holiday_overview_edit_op'),
    path('Company/Payroll/Holiday/Overview_comment/<int:pk>',views.company_holiday_overview_comment,name='company_holiday_overview_comment'),
    path('Company/Payroll/Holiday/Overview_comment_delete/<int:pk>',views.company_holiday_overview_comment_delete,name='company_holiday_overview_comment_delete'),
    path('Company/Payroll/Holiday/Overview_email_send',views.company_holiday_overview_email_send,name='company_holiday_overview_email_send'),
    



    # -------------------------------Staff section--------------------------------
    path('Staff/Dashboard',views.staff_dashboard,name='staff_dashboard'),
    path('Staff/Profile',views.staff_profile,name='staff_profile'),
    path('Staff/Profile-Editpage',views.staff_profile_editpage,name='staff_profile_editpage'),
    path('Staff/Profile/Edit/details',views.staff_profile_details_edit,name='staff_profile_details_edit'),
    path('Staff/Password_Change',views.staff_password_change,name='staff_password_change'),
    
    # -------------------------------Zoho Modules section--------------------------------
    
    
  
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)