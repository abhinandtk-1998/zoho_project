#Zoho Final
from django.shortcuts import render,redirect
from Register_Login.models import *
from Register_Login.views import logout
from django.contrib import messages
from django.conf import settings
from datetime import date
from datetime import datetime, timedelta
from Company_Staff.models import *
from django.db import models
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound, JsonResponse
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
from django.template.loader import get_template
from bs4 import BeautifulSoup
import io,os
import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
from django.http import HttpResponse,HttpResponseRedirect
from io import BytesIO
from django.db.models import Max
from django.db.models import Q
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
import calendar
from django.template.loader import render_to_string
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from django.urls import reverse
from reportlab.platypus import Spacer
from django.core.mail import EmailMultiAlternatives
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfgen import canvas



# Create your views here.



# -------------------------------Company section--------------------------------
# company dashboard
def company_dashboard(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')

        # Calculate the date 20 days before the end date for payment term renew and 10 days before for trial period renew
        if dash_details.payment_term:
            reminder_date = dash_details.End_date - timedelta(days=20)
        else:
            reminder_date = dash_details.End_date - timedelta(days=10)
        current_date = date.today()
        alert_message = current_date >= reminder_date
        
        payment_request = True if PaymentTermsUpdates.objects.filter(company=dash_details,update_action=1,status='Pending').exists() else False

        # Calculate the number of days between the reminder date and end date
        days_left = (dash_details.End_date - current_date).days
        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'alert_message':alert_message,
            'days_left':days_left,
            'payment_request':payment_request,
        }
        return render(request, 'company/company_dash.html', context)
    else:
        return redirect('/')
    
    
# def company_dashboard(request):
#     if 'login_id' in request.session:
#         log_id = request.session['login_id']
#         if 'login_id' not in request.session:
#             return redirect('/')
#         log_details= LoginDetails.objects.get(id=log_id)
#         dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
#         allmodules= ZohoModules.objects.get(company=dash_details,status='New')

#         # Calculate the date 20 days before the end date for payment term renew
#         reminder_date = dash_details.End_date - timedelta(days=20)
#         current_date = date.today()
#         alert_message = current_date >= reminder_date
        
#         payment_request = True if PaymentTermsUpdates.objects.filter(company=dash_details,update_action=1,status='Pending').exists() else False

#         # Calculate the number of days between the reminder date and end date
#         days_left = (dash_details.End_date - current_date).days
#         context = {
#             'details': dash_details,
#             'allmodules': allmodules,
#             'alert_message':alert_message,
#             'days_left':days_left,
#             'payment_request':payment_request,
#         }
#         return render(request, 'company/company_dash.html', context)
#     else:
#         return redirect('/')


# company staff request for login approval
def company_staff_request(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        staff_request=StaffDetails.objects.filter(company=dash_details.id, company_approval=0).order_by('-id')
        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'requests':staff_request,
        }
        return render(request, 'company/staff_request.html', context)
    else:
        return redirect('/')

# company staff accept or reject
def staff_request_accept(request,pk):
    staff=StaffDetails.objects.get(id=pk)
    staff.company_approval=1
    staff.save()
    return redirect('company_staff_request')

def staff_request_reject(request,pk):
    staff=StaffDetails.objects.get(id=pk)
    login_details=LoginDetails.objects.get(id=staff.company.id)
    login_details.delete()
    staff.delete()
    return redirect('company_staff_request')


# All company staff view, cancel staff approval
def company_all_staff(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        all_staffs=StaffDetails.objects.filter(company=dash_details.id, company_approval=1).order_by('-id')
       
        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'staffs':all_staffs,
        }
        return render(request, 'company/all_staff_view.html', context)
    else:
        return redirect('/')

def staff_approval_cancel(request, pk):
    """
    Sets the company approval status to 2 for the specified staff member, effectively canceling staff approval.

    This function is designed to be used for canceling staff approval, and the company approval value is set to 2.
    This can be useful for identifying resigned staff under the company in the future.

    """
    staff = StaffDetails.objects.get(id=pk)
    staff.company_approval = 2
    staff.save()
    return redirect('company_all_staff')


# company profile, profile edit
def company_profile(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        terms=PaymentTerms.objects.all()
        payment_history=dash_details.previous_plans.all()

        # Calculate the date 20 days before the end date
        reminder_date = dash_details.End_date - timedelta(days=20)
        current_date = date.today()
        renew_button = current_date >= reminder_date

        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'renew_button': renew_button,
            'terms':terms,
            'payment_history':payment_history,
        }
        return render(request, 'company/company_profile.html', context)
    else:
        return redirect('/')

def company_profile_editpage(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        context = {
            'details': dash_details,
            'allmodules': allmodules
        }
        return render(request, 'company/company_profile_editpage.html', context)
    else:
        return redirect('/')

def company_profile_basicdetails_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        if request.method == 'POST':
            # Get data from the form
            log_details.first_name = request.POST.get('fname')
            log_details.last_name = request.POST.get('lname')
            log_details.email = request.POST.get('eid')
            log_details.username = request.POST.get('uname')
            log_details.save()
            messages.success(request,'Updated')
            return redirect('company_profile_editpage') 
        else:
            return redirect('company_profile_editpage') 

    else:
        return redirect('/')
    
def company_password_change(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        if request.method == 'POST':
            # Get data from the form
            password = request.POST.get('pass')
            cpassword = request.POST.get('cpass')
            if password == cpassword:
                if LoginDetails.objects.filter(password=password).exists():
                    messages.error(request,'Use another password')
                    return redirect('company_profile_editpage')
                else:
                    log_details.password=password
                    log_details.save()

            messages.success(request,'Password Changed')
            return redirect('company_profile_editpage') 
        else:
            return redirect('company_profile_editpage') 

    else:
        return redirect('/')
       
def company_profile_companydetails_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details = LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)

        if request.method == 'POST':
            # Get data from the form
            gstno = request.POST.get('gstno')
            profile_pic = request.FILES.get('image')

            # Update the CompanyDetails object with form data
            dash_details.company_name = request.POST.get('cname')
            dash_details.contact = request.POST.get('phone')
            dash_details.address = request.POST.get('address')
            dash_details.city = request.POST.get('city')
            dash_details.state = request.POST.get('state')
            dash_details.country = request.POST.get('country')
            dash_details.pincode = request.POST.get('pincode')
            dash_details.pan_number = request.POST.get('pannumber')

            if gstno:
                dash_details.gst_no = gstno

            if profile_pic:
                dash_details.profile_pic = profile_pic

            dash_details.save()

            messages.success(request, 'Updated')
            return redirect('company_profile_editpage')
        else:
            return redirect('company_profile_editpage')
    else:
        return redirect('/')    

# company modules editpage
def company_module_editpage(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        context = {
            'details': dash_details,
            'allmodules': allmodules
        }
        return render(request, 'company/company_module_editpage.html', context)
    else:
        return redirect('/')

def company_module_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')

        # Check for any previous module update request
        if ZohoModules.objects.filter(company=dash_details,status='Pending').exists():
            messages.warning(request,'You have a pending update request, wait for approval or contact our support team for any help..?')
            return redirect('company_profile')
        if request.method == 'POST':
            # Retrieve values
            items = request.POST.get('items', 0)
            price_list = request.POST.get('price_list', 0)
            stock_adjustment = request.POST.get('stock_adjustment', 0)
            godown = request.POST.get('godown', 0)

            cash_in_hand = request.POST.get('cash_in_hand', 0)
            offline_banking = request.POST.get('offline_banking', 0)
            upi = request.POST.get('upi', 0)
            bank_holders = request.POST.get('bank_holders', 0)
            cheque = request.POST.get('cheque', 0)
            loan_account = request.POST.get('loan_account', 0)

            customers = request.POST.get('customers', 0)
            invoice = request.POST.get('invoice', 0)
            estimate = request.POST.get('estimate', 0)
            sales_order = request.POST.get('sales_order', 0)
            recurring_invoice = request.POST.get('recurring_invoice', 0)
            retainer_invoice = request.POST.get('retainer_invoice', 0)
            credit_note = request.POST.get('credit_note', 0)
            payment_received = request.POST.get('payment_received', 0)
            delivery_challan = request.POST.get('delivery_challan', 0)

            vendors = request.POST.get('vendors', 0)
            bills = request.POST.get('bills', 0)
            recurring_bills = request.POST.get('recurring_bills', 0)
            vendor_credit = request.POST.get('vendor_credit', 0)
            purchase_order = request.POST.get('purchase_order', 0)
            expenses = request.POST.get('expenses', 0)
            recurring_expenses = request.POST.get('recurring_expenses', 0)
            payment_made = request.POST.get('payment_made', 0)

            projects = request.POST.get('projects', 0)

            chart_of_accounts = request.POST.get('chart_of_accounts', 0)
            manual_journal = request.POST.get('manual_journal', 0)

            eway_bill = request.POST.get('ewaybill', 0)

            employees = request.POST.get('employees', 0)
            employees_loan = request.POST.get('employees_loan', 0)
            holiday = request.POST.get('holiday', 0)
            attendance = request.POST.get('attendance', 0)
            salary_details = request.POST.get('salary_details', 0)

            reports = request.POST.get('reports', 0)

            update_action=1
            status='Pending'

            # Create a new ZohoModules instance and save it to the database
            data = ZohoModules(
                company=dash_details,
                items=items, price_list=price_list, stock_adjustment=stock_adjustment, godown=godown,
                cash_in_hand=cash_in_hand, offline_banking=offline_banking, upi=upi, bank_holders=bank_holders,
                cheque=cheque, loan_account=loan_account,
                customers=customers, invoice=invoice, estimate=estimate, sales_order=sales_order,
                recurring_invoice=recurring_invoice, retainer_invoice=retainer_invoice, credit_note=credit_note,
                payment_received=payment_received, delivery_challan=delivery_challan,
                vendors=vendors, bills=bills, recurring_bills=recurring_bills, vendor_credit=vendor_credit,
                purchase_order=purchase_order, expenses=expenses, recurring_expenses=recurring_expenses,
                payment_made=payment_made,
                projects=projects,
                chart_of_accounts=chart_of_accounts, manual_journal=manual_journal,
                eway_bill=eway_bill,
                employees=employees, employees_loan=employees_loan, holiday=holiday,
                attendance=attendance, salary_details=salary_details,
                reports=reports,update_action=update_action,status=status    
            )
            data.save()
            messages.success(request,"Request sent successfully. Please wait for approval.")
            return redirect('company_profile')
        else:
            return redirect('company_module_editpage')  
    else:
        return redirect('/')


def company_renew_terms(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)

        # Check for any previous  extension request
        if PaymentTermsUpdates.objects.filter(company=dash_details,update_action=1,status='Pending').exists():
            messages.warning(request,'You have a pending request, wait for approval or contact our support team for any help..?')
            return redirect('company_profile')
        if request.method == 'POST':
            select=request.POST['select']
            terms=PaymentTerms.objects.get(id=select)
            update_action=1
            status='Pending'
            newterms=PaymentTermsUpdates(
               company=dash_details,
               payment_term=terms,
               update_action=update_action,
               status=status 
            )
            newterms.save()
            messages.success(request,'Request sent successfully, Please wait for approval...')
            return redirect('company_profile')
        else:
            return redirect('company_profile')
    else:
        return redirect('/')

# company notifications and messages
def company_notifications(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        notifications = dash_details.notifications.filter(is_read=0).order_by('-date_created','-time')
        end_date = dash_details.End_date
        company_days_remaining = (end_date - date.today()).days
        payment_request = True if PaymentTermsUpdates.objects.filter(company=dash_details,update_action=1,status='Pending').exists() else False
        
        print(company_days_remaining)
        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'notifications':notifications,
            'days_remaining':company_days_remaining,
            'payment_request':payment_request,
        }

        return render(request,'company/company_notifications.html',context)
        
    else:
        return redirect('/')
        
        
def company_message_read(request,pk):
    '''
    message read functions set the is_read to 1, 
    by default it is 0 means not seen by user.

    '''
    notification=Notifications.objects.get(id=pk)
    notification.is_read=1
    notification.save()
    return redirect('company_notifications')
    
    
def company_payment_history(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/') 
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        payment_history=dash_details.previous_plans.all()

        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'payment_history':payment_history,
            
        }
        return render(request,'company/company_payment_history.html', context)
    else:
        return redirect('/')
        
def company_trial_feedback(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/') 
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        trial_instance = TrialPeriod.objects.get(company=dash_details)
        if request.method == 'POST':
            interested = request.POST.get('interested')
            feedback=request.POST.get('feedback') 
            
            trial_instance.interested_in_buying=1 if interested =='yes' else 2
            trial_instance.feedback=feedback
            trial_instance.save()

            if interested =='yes':
                return redirect('company_profile')
            else:
                return redirect('company_dashboard')
        else:
            return redirect('company_dashboard')
    else:
        return redirect('/')
    
#company holiday
    
def company_holiday(request):

    if 'login_id' in request.session:
        log_id = request.session['login_id']

        login_d = LoginDetails.objects.get(id=log_id)
        if login_d.user_type == 'Company':
            company_id = CompanyDetails.objects.get(login_details=login_d)
            dash_details = CompanyDetails.objects.get(login_details=login_d,superadmin_approval=1,Distributor_approval=1)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            

            month_list = []
            year_list = []
            date_list = []

            holiday_list = Holiday.objects.filter(company=company_id)

            # making list of all dates which are hoidays
            for d in holiday_list:
                current_date = d.start_date
                while current_date <= d.end_date:
                    if current_date not in date_list:
                        date_list.append(current_date)
                    current_date += timedelta(days=1)



            for  d in date_list:
                if d.strftime("%B") not in month_list:
                    month_list.append(d.strftime("%B"))

                if d.year not in year_list:
                    year_list.append(d.year)

            # year_list.sort()

            month30 = ["April", "June", "September", "November"]
            month31 = ["January", "March", "May", "July", "August", "October", "December"]

            holiday_table = {}
            
            i = 1
            for y in year_list:
                for m in month_list:
                    holiday_c = 0
                    st = 0
                    for h in date_list:
                        if m == h.strftime("%B") and y == h.year:
                            holiday_c = holiday_c + 1
                            st = 1

                    if st == 1:
                    
                        if m in month31:
                            working_days = 31 - holiday_c
                        elif m in month30:
                            working_days = 30 - holiday_c
                        else:
                            if calendar.isleap(y):
                                working_days = 29 - holiday_c

                            else:
                                working_days = 28 - holiday_c

                        holiday_table[i] = [i, m, y, holiday_c, working_days]
                        i = i + 1
                        st = 0

            dash_status = 0

            context = {
                'holiday_table':holiday_table,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,
            }


                
            return render(request,'company/company_holiday.html', context)
        
        if login_d.user_type == 'Staff':
            staff_d = StaffDetails.objects.get(login_details=login_d)
            dash_details = StaffDetails.objects.get(login_details=login_d,company_approval=1)
            allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
            

            month_list = []
            year_list = []
            date_list = []

            holiday_list = Holiday.objects.filter(company=staff_d.company)

            # making list of all dates which are hoidays
            for d in holiday_list:
                current_date = d.start_date
                while current_date <= d.end_date:
                    if current_date not in date_list:
                        date_list.append(current_date)
                    current_date += timedelta(days=1)



            for  d in date_list:
                if d.strftime("%B") not in month_list:
                    month_list.append(d.strftime("%B"))

                if d.year not in year_list:
                    year_list.append(d.year)

            # year_list.sort()

            month30 = ["April", "June", "September", "November"]
            month31 = ["January", "March", "May", "July", "August", "October", "December"]

            holiday_table = {}
            
            i = 1
            for y in year_list:
                for m in month_list:
                    holiday_c = 0
                    st = 0
                    for h in date_list:
                        if m == h.strftime("%B") and y == h.year:
                            holiday_c = holiday_c + 1
                            st = 1

                    if st == 1:
                    
                        if m in month31:
                            working_days = 31 - holiday_c
                        elif m in month30:
                            working_days = 30 - holiday_c
                        else:
                            if calendar.isleap(y):
                                working_days = 29 - holiday_c

                            else:
                                working_days = 28 - holiday_c

                        holiday_table[i] = [i, m, y, holiday_c, working_days]
                        i = i + 1
                        st = 0
            dash_status = 1

            context = {
                'holiday_table':holiday_table,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,
            }

                
            return render(request,'company/company_holiday.html', context)
        

    
    else:
        return redirect('/')


def company_holiday_new(request):

    if 'login_id' in request.session:
        log_id = request.session['login_id']
    
        
        login_d = LoginDetails.objects.get(id=log_id)
        if login_d.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=login_d,superadmin_approval=1,Distributor_approval=1)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')

            # value of n deside holiday page or overview page after holiday addition
            n = request.GET.get('n')

            dash_status = 0
            context = {
                'n':n,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,
            }
            return render(request,'company/company_holiday_new.html', context)
        
        if login_d.user_type == 'Staff':
            dash_details = StaffDetails.objects.get(login_details=login_d,company_approval=1)
            allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')

            # value of n deside holiday page or overview page after holiday addition
            n = request.GET.get('n')

            dash_status = 1
            context = {
                'n':n,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,

            }
            return render(request,'company/company_holiday_new.html', context)
    
    else:
        return redirect('/')

def company_holiday_new_add(request):

    if 'login_id' in request.session:
        log_id = request.session['login_id']
        
        login_d = LoginDetails.objects.get(id=log_id)
        if login_d.user_type == 'Company':
            company_id = CompanyDetails.objects.get(login_details=login_d)
            if request.method=="POST":
                dest=request.POST['destination']
                title=request.POST['title']
                s_date=request.POST['sdate']
                e_date=request.POST['edate']

                if e_date < s_date:
                    messages.info(request, "End date cannot be earlier than start date")
                    return redirect(reverse('company_holiday_new') + f'?n={dest}')

                if Holiday.objects.filter(start_date=s_date,end_date=e_date,holiday_name=title,company=company_id).exists():
                    messages.info(request, 'This holiday already exists')
                    return redirect(reverse('company_holiday_new') + f'?n={dest}')

                holiday_d = Holiday(start_date=s_date,end_date=e_date,holiday_name=title,user=login_d,company=company_id)
                holiday_d.save()

                today_date = date.today()
                action_h = "Created"

                history = Holiday_history(company=company_id,user=login_d,holiday=holiday_d,date=today_date,action=action_h)
                history.save()

                dest1 = int(dest)

                # to overview page
                if dest1 == 1:
                    return redirect('company_holiday_overview')
                
                #to holiday page
                else:
                    return redirect('company_holiday')
            
            return redirect('company_holiday_new')
        
        
        

        if login_d.user_type == 'Staff':
            staff_id = StaffDetails.objects.get(login_details=login_d)
            if request.method=="POST":
                dest=request.POST['destination']
                title=request.POST['title']
                s_date=request.POST['sdate']
                e_date=request.POST['edate']

                if e_date < s_date:
                    messages.info(request, "End date cannot be earlier than start date")
                    return redirect(reverse('company_holiday_new') + f'?n={dest}')

                if Holiday.objects.filter(start_date=s_date,end_date=e_date,holiday_name=title,company=staff_id.company).exists():
                    messages.info(request, 'This holiday already exists')
                    return redirect(reverse('company_holiday_new') + f'?n={dest}')

                holiday_d = Holiday(start_date=s_date,end_date=e_date,holiday_name=title,user=login_d,company=staff_id.company)
                holiday_d.save()

                today_date = date.today()
                action_h = "Created"

                history = Holiday_history(company=staff_id.company,user=login_d,holiday=holiday_d,date=today_date,action=action_h)
                history.save()


                dest1 = int(dest)

                # to overview page
                if dest1 == 1:
                    return redirect('company_holiday_overview')
                
                #to holiday page
                else:
                    return redirect('company_holiday')
            
            return redirect('company_holiday_new')
        
        
    
    else:
        return redirect('/')


def company_holiday_import_sample_download(request):
     # Path to the sample Excel file
    file_path = os.path.join(settings.BASE_DIR, 'static', 'holiday_sample_files', 'sample.xlsx')
    print(file_path)
    try:
        # Open the file
        with open(file_path, 'rb') as excel_file:
            # Return the file as response
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="sample.xlsx"'
            return response
    except FileNotFoundError:
        # Handle file not found error
        return HttpResponse("File not found", status=404)
    except Exception as e:
        # Handle other exceptions
        return HttpResponse("An error occurred", status=500)

    
def company_holiday_import_operation(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        

        login_d = LoginDetails.objects.get(id=log_id)
        if login_d.user_type == 'Company':
            company_id = CompanyDetails.objects.get(login_details=login_d)
            if request.method == 'POST' and request.FILES['file']:
                excel_file = request.FILES['file']

                # Check if the uploaded file is an Excel file
                if excel_file.name.endswith('.xls') or excel_file.name.endswith('.xlsx'):
                    # Load Excel file into pandas DataFrame
                    df = pd.read_excel(excel_file)

                    # Iterate through rows and save data to database
                    for index, row in df.iterrows():
                        # Create a new object of YourModel and populate fields
                        if Holiday.objects.filter(start_date=row['s_date'],end_date=row['e_date'],holiday_name=row['title'],user=login_d,company=company_id).exists():
                            continue
                        if row['s_date'] > row['e_date']:
                            continue
                        
                        h1 = Holiday(
                            holiday_name=row['title'],
                            start_date=row['s_date'],
                            end_date=row['e_date'],
                            user=login_d,
                            company=company_id,
                        )
                        h1.save()

                        today_date = date.today()
                        action_h = "Created"

                        history = Holiday_history(company=company_id,user=login_d,holiday=h1,date=today_date,action=action_h)
                        history.save()

                    # Redirect to a success page or render a success message
                    return redirect('company_holiday')

            # Render the upload form
            return redirect('company_holiday_import')
        
        if login_d.user_type == 'Staff':
            staff_id = StaffDetails.objects.get(login_details=login_d)
            if request.method == 'POST' and request.FILES['file']:
                excel_file = request.FILES['file']

                # Check if the uploaded file is an Excel file
                if excel_file.name.endswith('.xls') or excel_file.name.endswith('.xlsx'):
                    # Load Excel file into pandas DataFrame
                    df = pd.read_excel(excel_file)

                    # Iterate through rows and save data to database
                    for index, row in df.iterrows():
                        # Create a new object of YourModel and populate fields
                        if Holiday.objects.filter(start_date=row['s_date'],end_date=row['e_date'],holiday_name=row['title'],user=login_d,company=staff_id.company).exists():
                            continue
                        if row['s_date'] > row['e_date']:
                            continue
                        
                        h1 = Holiday(
                            holiday_name=row['title'],
                            start_date=row['s_date'],
                            end_date=row['e_date'],
                            user=login_d,
                            company=staff_id.company,
                        )
                        h1.save()

                        today_date = date.today()
                        action_h = "Created"

                        history = Holiday_history(company=staff_id.company,user=login_d,holiday=h1,date=today_date,action=action_h)
                        history.save()

                    # Redirect to a success page or render a success message
                    return redirect('company_holiday')

            # Render the upload form
            return redirect('company_holiday_import')
    
    else:
        return redirect('/')

def company_holiday_overview(request):

    if 'login_id' in request.session:
        log_id = request.session['login_id']

        login_d = LoginDetails.objects.get(id=log_id)

        if login_d.user_type == 'Company':

            company_id = CompanyDetails.objects.get(login_details=login_d)
            comment = Comment_holiday.objects.filter(company=company_id)
            holiday_history = Holiday_history.objects.filter(company=company_id)
            dash_details = CompanyDetails.objects.get(login_details=login_d,superadmin_approval=1,Distributor_approval=1)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')

            mn = request.GET.get('month')
            yr = request.GET.get('year')

            #default view of tab view depend on togd, 1-list, else-calendar
            togd = request.GET.get('togd')

            holiday2 = Holiday.objects.filter(company=company_id)

            for h3 in holiday2:
                mn2 = h3.start_date.strftime("%B")
                yr2 = h3.start_date.year
                break
            

            if mn is None:
                mn = mn2
            if yr is None:
                yr = yr2
                
            try:
                month = datetime.strptime(mn, '%B').month
            except:
                month = mn

            year = int(yr)

            events = Holiday.objects.filter(Q(start_date__month=month, start_date__year=year, company=company_id) | Q(end_date__month=month, end_date__year=year, company=company_id))

            event_list = {}

            k = 1
            for e1 in events:
                current_date = e1.start_date
                while current_date <= e1.end_date:
                    event_list[k] = [k, e1.holiday_name, current_date ]
                    k = k + 1
                    current_date += timedelta(days=1)
                


            event_table = {}
            j = 1

            for h in events:
                event_table[j] = [j, h.holiday_name, h.start_date, h.end_date, h.id]
                j = j + 1

            month_list = []
            year_list = []
            date_list = []
            holiday_list = Holiday.objects.filter(company=company_id)
            for d in holiday_list:
                current_date = d.start_date
                while current_date <= d.end_date:
                    if current_date not in date_list:
                        date_list.append(current_date)
                    current_date += timedelta(days=1)



            for  d in date_list:
                if d.strftime("%B") not in month_list:
                    month_list.append(d.strftime("%B"))

                if d.year not in year_list:
                    year_list.append(d.year)


            holiday_table = {}
            
            i = 1
            for y in year_list:
                for m in month_list:
                    holiday_c = 0
                    st = 0
                    for h in date_list:
                        if m == h.strftime("%B") and y == h.year:
                            holiday_c = holiday_c + 1
                            st = 1

                    if st == 1:
                    

                        holiday_table[i] = [i, m, y, holiday_c]
                        i = i + 1
                        st = 0


            month_name = datetime.strptime(str(month), '%m').strftime('%B')

            
            dash_status = 0
            

            context = {
                'holiday_table':holiday_table,
                'events':events,
                'event_list':event_list,
                'event_table':event_table,
                'month_name':month_name,
                'month':month,
                'year':year,
                'comments':comment,
                'holiday_history':holiday_history,
                'togd':togd,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,
            }

            return render(request, 'company/company_holiday_overview.html',context)
        
        if login_d.user_type == 'Staff':
            staff_id = StaffDetails.objects.get(login_details=login_d)
            comment = Comment_holiday.objects.filter(company=staff_id.company)
            holiday_history = Holiday_history.objects.filter(company=staff_id.company)
            dash_details = StaffDetails.objects.get(login_details=login_d,company_approval=1)
            allmodules= ZohoModules.objects.get(company=staff_id.company,status='New')

            mn = request.GET.get('month')
            yr = request.GET.get('year')

            #default view of tab view depend on togd, 1-list, else-calendar
            togd = request.GET.get('togd')

            holiday2 = Holiday.objects.filter(company=staff_id.company)

            for h3 in holiday2:
                mn2 = h3.start_date.strftime("%B")
                yr2 = h3.start_date.year
                break
            

            if mn is None:
                mn = mn2
            if yr is None:
                yr = yr2
                
            try:
                month = datetime.strptime(mn, '%B').month
            except:
                month = mn

            year = int(yr)

            events = Holiday.objects.filter(Q(start_date__month=month, start_date__year=year, company=staff_id.company) | Q(end_date__month=month, end_date__year=year, company=staff_id.company))

            event_list = {}

            k = 1
            for e1 in events:
                current_date = e1.start_date
                while current_date <= e1.end_date:
                    event_list[k] = [k, e1.holiday_name, current_date ]
                    k = k + 1
                    current_date += timedelta(days=1)
                


            event_table = {}
            j = 1

            for h in events:
                event_table[j] = [j, h.holiday_name, h.start_date, h.end_date, h.id]
                j = j + 1

            month_list = []
            year_list = []
            date_list = []
            holiday_list = Holiday.objects.filter(company=staff_id.company)
            for d in holiday_list:
                current_date = d.start_date
                while current_date <= d.end_date:
                    if current_date not in date_list:
                        date_list.append(current_date)
                    current_date += timedelta(days=1)



            for  d in date_list:
                if d.strftime("%B") not in month_list:
                    month_list.append(d.strftime("%B"))

                if d.year not in year_list:
                    year_list.append(d.year)


            holiday_table = {}
            
            i = 1
            for y in year_list:
                for m in month_list:
                    holiday_c = 0
                    st = 0
                    for h in date_list:
                        if m == h.strftime("%B") and y == h.year:
                            holiday_c = holiday_c + 1
                            st = 1

                    if st == 1:
                    

                        holiday_table[i] = [i, m, y, holiday_c]
                        i = i + 1
                        st = 0


            month_name = datetime.strptime(str(month), '%m').strftime('%B')

            
            dash_status = 1
            

            context = {
                'holiday_table':holiday_table,
                'events':events,
                'event_list':event_list,
                'event_table':event_table,
                'month_name':month_name,
                'month':month,
                'year':year,
                'comments':comment,
                'holiday_history':holiday_history,
                'togd':togd,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,
            }

            return render(request, 'company/company_holiday_overview.html',context)
    
    else:
        return redirect('/')


def company_holiday_overview_delete(request,pk):

    h1 = Holiday.objects.get(id=pk)
    history_h = Holiday_history.objects.filter(holiday=pk)

    year1 = request.GET.get('year')
    month1 = request.GET.get('month')

    h1.delete()
    for h in history_h:
        h.delete()

    togd=1
    
    return redirect(reverse('company_holiday_overview') + f'?month={month1}&year={year1}&togd={togd}')


def company_holiday_overview_edit(request,pk):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
    
        login_d = LoginDetails.objects.get(id=log_id)

        if login_d.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=login_d,superadmin_approval=1,Distributor_approval=1)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')

            year = request.GET.get('year')
            month = request.GET.get('month')

            h1 = Holiday.objects.get(id=pk)

            dash_status = 0

            context = {
                'id':pk,
                'holiday':h1,
                'month':month,
                'year':year,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,
            }
            return render(request, 'company/company_holiday_overview_edit.html',context)
        
        if login_d.user_type == 'Staff':
            dash_details = StaffDetails.objects.get(login_details=login_d,company_approval=1)
            allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')

            year = request.GET.get('year')
            month = request.GET.get('month')

            h1 = Holiday.objects.get(id=pk)

            dash_status = 1
            context = {
                'id':pk,
                'holiday':h1,
                'month':month,
                'year':year,
                'details': dash_details,
                'allmodules': allmodules,
                'dash_status':dash_status,
            }
            return render(request, 'company/company_holiday_overview_edit.html',context)
    else:
        return redirect('/')

def company_holiday_overview_edit_op(request,pk):
    if 'login_id' in request.session:
        log_id = request.session['login_id']

        login_d = LoginDetails.objects.get(id=log_id)

        if login_d.user_type == 'Company':
        
            company_id = CompanyDetails.objects.get(login_details=login_d)

            year = request.GET.get('year')
            month = request.GET.get('month')


            if request.method=="POST":
                title=request.POST['title']
                s_date=request.POST['sdate']
                e_date=request.POST['edate']

                if s_date > e_date:
                    messages.info(request, "End date cannot be earlier than start date")
                    return redirect(reverse('company_holiday_overview_edit', kwargs={'pk': pk}) + f'?month={month}&year={year}')


                holiday_d = Holiday.objects.get(id=pk)

                togd = 1

                st_date = datetime.strptime(s_date, '%Y-%m-%d').date()
                et_date = datetime.strptime(e_date, '%Y-%m-%d').date()

                if holiday_d.holiday_name == title and holiday_d.start_date == st_date and holiday_d.end_date == et_date:
                    return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')

                holiday_d.holiday_name = title
                holiday_d.start_date = s_date
                holiday_d.end_date = e_date

                today_date = date.today()
                action_h = "Edited"

                history_h = Holiday_history(company=company_id,user=login_d,holiday=holiday_d,date=today_date,action=action_h)
                


                holiday_d.save()
                history_h.save()
                
                togd = 1

                
                return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
            
        if login_d.user_type == 'Staff':
    
            staff_id = StaffDetails.objects.get(login_details=login_d)

            year = request.GET.get('year')
            month = request.GET.get('month')


            if request.method=="POST":
                title=request.POST['title']
                s_date=request.POST['sdate']
                e_date=request.POST['edate']

                if s_date > e_date:
                    messages.info(request, "End date cannot be earlier than start date")
                    return redirect(reverse('company_holiday_overview_edit', kwargs={'pk': pk}) + f'?month={month}&year={year}')


                holiday_d = Holiday.objects.get(id=pk)

                togd = 1


                st_date = datetime.strptime(s_date, '%Y-%m-%d').date()
                et_date = datetime.strptime(e_date, '%Y-%m-%d').date()

                if holiday_d.holiday_name == title and holiday_d.start_date == st_date and holiday_d.end_date == et_date:
                    return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')


                holiday_d.holiday_name = title
                holiday_d.start_date = s_date
                holiday_d.end_date = e_date

                today_date = date.today()
                action_h = "Edited"

                history_h = Holiday_history(company=staff_id.company,user=login_d,holiday=holiday_d,date=today_date,action=action_h)
                


                holiday_d.save()
                history_h.save()
                togd = 1

                
                return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
            
        else:
            return redirect('/')

    
    return redirect('company_holiday_overview_edit')

def company_holiday_overview_comment(request,pk):
    if 'login_id' in request.session:
        log_id = request.session['login_id']


        login_d = LoginDetails.objects.get(id=log_id)

        if login_d.user_type == 'Company':
            company_id = CompanyDetails.objects.get(login_details=login_d)

            month = request.GET.get('month')
            year = request.GET.get('year')

            togd = 1

            if request.method=='POST':
                comment=request.POST['comment']

                holiday = Holiday.objects.get(id=pk)

                c1 = Comment_holiday(holiday_details=holiday, comment=comment, user=login_d, company=company_id)
                c1.save()

                return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
            
            return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
        
        if login_d.user_type == 'Staff':
            staff_id = StaffDetails.objects.get(login_details=login_d)

            month = request.GET.get('month')
            year = request.GET.get('year')

            togd = 1

            if request.method=='POST':
                comment=request.POST['comment']

                holiday = Holiday.objects.get(id=pk)

                c1 = Comment_holiday(holiday_details=holiday, comment=comment, user=login_d, company=staff_id.company)
                c1.save()

                return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
            
            return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
    else:
        return redirect('/')

def company_holiday_overview_comment_delete(request,pk):
    month = request.GET.get('month')
    year = request.GET.get('year')
    c1 = Comment_holiday.objects.get(id=pk)
    c1.delete()
    togd = 1

    return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')






def company_holiday_overview_email_send(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']


        login_d = LoginDetails.objects.get(id=log_id)

        if login_d.user_type == 'Company':


            company_id = CompanyDetails.objects.get(login_details=login_d)
            month = request.GET.get('mn')
            year = request.GET.get('yr')
            month_name = calendar.month_name[int(month)]
            eaddress = request.POST.get('email')  # Get email address from POST request

            if request.method=="POST":

                h1 = Holiday.objects.filter(Q(start_date__month=month, start_date__year=year, company=company_id) | Q(end_date__month=month, end_date__year=year, company=company_id))
                holiday_d = {}
                j = 1

                for h in h1:
                    holiday_d[j] = [h.holiday_name, h.start_date, h.end_date]
                    j += 1

                # Create a PDF document
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

                # Create a heading
                heading_text = f"<b>{month_name} {year}</b>"
                heading_style = ParagraphStyle(name='Heading1', alignment=1, fontSize=20)
                heading = Paragraph(heading_text, heading_style)

                # Create a list to hold all the data rows
                table_data = []

                # Add header row
                headers = ['Sl No', 'Holiday Name', 'Start Date', 'End Date']
                table_data.append(headers)

                # Extract keys and values from the dictionary
                keys = list(holiday_d.keys())
                values = list(holiday_d.values())

                # Add keys as the first column
                keys_column = [[str(key)] for key in keys]

                # Combine keys column with values
                for i in range(len(values)):
                    row = keys_column[i] + values[i]
                    table_data.append(row)

                # Create a table from the data
                table = Table(table_data)

                # Style the table
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 12)  # Increase font size for table data
                ])
                table.setStyle(style)

                # Add space before the table
                spacer = Spacer(1, 20)  # Add 20 points of space before the table

                # Build the PDF document
                elements = [heading, spacer, table]
                doc.build(elements)

                pdf_buffer.seek(0)

                # Send the email with the PDF attachment
                subject = "Holiday List"
                message = "Please find the attached holiday list."
                recipient = eaddress

                msg = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [recipient])
                msg.attach("holiday_list.pdf", pdf_buffer.read(), 'application/pdf')
                msg.send()

                togd = 1
                return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
            
        if login_d.user_type == 'Staff':


            staff_id = StaffDetails.objects.get(login_details=login_d)
            month = request.GET.get('mn')
            year = request.GET.get('yr')
            month_name = calendar.month_name[int(month)]
            eaddress = request.POST.get('email')  # Get email address from POST request

            if request.method=="POST":

                h1 = Holiday.objects.filter(Q(start_date__month=month, start_date__year=year, company=staff_id.company) | Q(end_date__month=month, end_date__year=year, company=staff_id.company))
                holiday_d = {}
                j = 1

                for h in h1:
                    holiday_d[j] = [h.holiday_name, h.start_date, h.end_date]
                    j += 1

                # Create a PDF document
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

                # Create a heading
                heading_text = f"<b>{month_name} {year}</b>"
                heading_style = ParagraphStyle(name='Heading1', alignment=1, fontSize=20)
                heading = Paragraph(heading_text, heading_style)

                # Create a list to hold all the data rows
                table_data = []

                # Add header row
                headers = ['Sl No', 'Holiday Name', 'Start Date', 'End Date']
                table_data.append(headers)

                # Extract keys and values from the dictionary
                keys = list(holiday_d.keys())
                values = list(holiday_d.values())

                # Add keys as the first column
                keys_column = [[str(key)] for key in keys]

                # Combine keys column with values
                for i in range(len(values)):
                    row = keys_column[i] + values[i]
                    table_data.append(row)

                # Create a table from the data
                table = Table(table_data)

                # Style the table
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 12)  # Increase font size for table data
                ])
                table.setStyle(style)

                # Add space before the table
                spacer = Spacer(1, 20)  # Add 20 points of space before the table

                # Build the PDF document
                elements = [heading, spacer, table]
                doc.build(elements)

                pdf_buffer.seek(0)

                # Send the email with the PDF attachment
                subject = "Holiday List"
                message = "Please find the attached holiday list."
                recipient = eaddress

                msg = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [recipient])
                msg.attach("holiday_list.pdf", pdf_buffer.read(), 'application/pdf')
                msg.send()

                togd = 1
                return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
            

        else:
            return redirect('/')
            



# def company_holiday_overview_email_send(request):

#     login_id = request.session['login_id']
#     login_d = LoginDetails.objects.get(id=login_id)
#     company_id = CompanyDetails.objects.get(login_details=login_d)
#     month = request.GET.get('mn')
#     year = request.GET.get('yr')
#     month_name = calendar.month_name[int(month)]
    
#     if request.method=="POST":
#         eaddress=request.POST['email']
#         h1 = Holiday.objects.filter(start_date__month=month,start_date__year=year,user=login_d,company=company_id)
#         holiday_d = {}
#         j = 1

#         for h in h1:
#             holiday_d[j] = [h.holiday_name, h.start_date, h.end_date]
#             j = j + 1

#          # Create a PDF document
#         pdf_file_name = "holiday_table.pdf"
#         doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)

#          # Create a heading
#         heading_text = f"<b> {month_name} {year}</b>"
#         heading_style = ParagraphStyle(name='Heading1', alignment=1, fontSize=20)
#         heading = Paragraph(heading_text, heading_style)

#         # Create a list to hold all the data rows
#         table_data = []

#         # Add header row
#         headers = ['Sl No', 'Holiday Name', 'Start Date', 'End Date']
#         table_data.append(headers)

#         # Extract keys and values from the dictionary
#         keys = list(holiday_d.keys())
#         values = list(holiday_d.values())


#         # Add keys as the first column
#         keys_column = [[str(key)] for key in keys]

#         # Combine keys column with values
#         for i in range(len(values)):
#             row = keys_column[i] + values[i]
#             table_data.append(row)

    

#         # Create a table from the data
#         table = Table(table_data)

#         # Style the table
#         style = TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#             ('GRID', (0, 0), (-1, -1), 1, colors.black),
#             ('FONTSIZE', (0, 0), (-1, -1), 12)  # Increase font size for table data
#         ])

#         table.setStyle(style)

#         # Add space before the table
#         spacer = Spacer(1, 20)  # Add 20 points of space before the table

#         # Build the PDF document
#         elements = [heading, spacer, table]
#         doc.build(elements)


#         subject = "Holiday List"
#         message = "Please find the attached holiday list."
#         recipient = eaddress

#         email = EmailMessage(
#             subject=subject,
#             body=message,
#             from_email=settings.EMAIL_HOST_USER,
#             to=[recipient]
#         )
        
#         # Attach the PDF file to the email
#         with open(pdf_file_name, 'rb') as pdf_file:
#             pdf_content = pdf_file.read()

#         # Attach the PDF file to the email
#         email.attach(pdf_file_name, pdf_content, 'application/pdf')

#         email.send()


#         togd = 1

#         return redirect(reverse('company_holiday_overview') + f'?month={month}&year={year}&togd={togd}')
    



    








# -------------------------------Staff section--------------------------------

# staff dashboard
def staff_dashboard(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
        context={
            'details':dash_details,
            'allmodules': allmodules,
        }
        return render(request,'staff/staff_dash.html',context)
    else:
        return redirect('/')


# staff profile
def staff_profile(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
        context={
            'details':dash_details,
            'allmodules': allmodules,
        }
        return render(request,'staff/staff_profile.html',context)
    else:
        return redirect('/')


def staff_profile_editpage(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
        context = {
            'details': dash_details,
            'allmodules': allmodules
        }
        return render(request, 'staff/staff_profile_editpage.html', context)
    else:
        return redirect('/')

def staff_profile_details_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        if request.method == 'POST':
            # Get data from the form
            log_details.first_name = request.POST.get('fname')
            log_details.last_name = request.POST.get('lname')
            log_details.email = request.POST.get('eid')
            log_details.username = request.POST.get('uname')
            log_details.save()
            dash_details.contact = request.POST.get('phone')
            old=dash_details.image
            new=request.FILES.get('profile_pic')
            print(new,old)
            if old!=None and new==None:
                dash_details.image=old
            else:
                print(new)
                dash_details.image=new
            dash_details.save()
            messages.success(request,'Updated')
            return redirect('staff_profile_editpage') 
        else:
            return redirect('staff_profile_editpage') 

    else:
        return redirect('/')

def staff_password_change(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        if request.method == 'POST':
            # Get data from the form
            password = request.POST.get('pass')
            cpassword = request.POST.get('cpass')
            if password == cpassword:
                if LoginDetails.objects.filter(password=password).exists():
                    messages.error(request,'Use another password')
                    return redirect('staff_profile_editpage')
                else:
                    log_details.password=password
                    log_details.save()

            messages.success(request,'Password Changed')
            return redirect('staff_profile_editpage') 
        else:
            return redirect('staff_profile_editpage') 

    else:
        return redirect('/')


    
def company_gsttype_change(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details = LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)

        if request.method == 'POST':
            # Get data from the form
            
            gstno = request.POST.get('gstno')
            gsttype = request.POST.get('gsttype')

            # Check if gsttype is one of the specified values
            if gsttype in ['unregistered Business', 'Overseas', 'Consumer']:
                dash_details.gst_no = None
            else:
                if gstno:
                    dash_details.gst_no = gstno
                else:
                    messages.error(request,'GST Number is not entered*')
                    return redirect('company_profile_editpage')


            dash_details.gst_type = gsttype

            dash_details.save()
            messages.success(request,'GST Type changed')
            return redirect('company_profile_editpage')
        else:
            return redirect('company_profile_editpage')
    else:
        return redirect('/') 
    

# -------------------------------Zoho Modules section--------------------------------
