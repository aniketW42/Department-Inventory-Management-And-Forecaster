from django.urls import path
from .maintenance_views import *
from .auth_views import *
from .dashboard_views import *
from .request_views import *
from .item_views import *
from .forecast_views import *
from .report_views import *

urlpatterns = [
    # Home and Authentication
    path('', home, name='home'),
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout'),

    # Dashboards
    path('faculty-dashboard/', faculty_dashboard, name='faculty_dashboard'),
    path('clerk-dashboard/', clerk_dashboard, name='clerk_dashboard'),
    path('hod-dashboard/', hod_dashboard, name='hod_dashboard'),

    # Requests Management
    path('manage-requests/', manage_requests, name='manage_requests'),
    path('process-request/<int:request_id>/', process_request, name='process_request'),
    path('view-all-requests/', view_all_requests, name='view_all_requests'),
    path('view_requests/<int:user_id>', view_requests, name='view_requests'),
    path('request-history/', request_history, name='request_history'),
    path('request-item/', request_item_page, name='request_item'),
    path('submit-request/', submit_item_request, name='request_item_submit'),

    # Items Management
    path('inventory-items', show_all_items, name='inventory_items'),
    path('items/add/', add_item, name='add_item'),
    path('items/edit/<int:pk>/', edit_item, name='edit_item'),
    path('delete-item/<int:pk>/', delete_item, name='delete_item'),
    path('issue-items/', issue_items, name='issue_items'),
    path('issue-items/<int:request_id>/mark/', mark_as_issued, name='mark_as_issued'),

    # Forecasting
    path('predict-usage/<int:year>', predict_usage, name='predict_usage'),
    path('forecast/', inventory_forecast_view, name='inventory_forecast'),
    path('predict-usage/next-year', forecast_inventory_usage, name = 'forecast_directly'),
    path('generate-forecast-excel/', generate_forecast_excel_report, name='generate_forecast_excel_report'),

    # User Management
    path('create-user/', create_user, name='create_user'),
    path('manage-users/', manage_users, name='manage_users'),

    # Reports
    path('reports/', reports, name='reports'),
    path('item-request-report/', item_request_report, name='item_request_report'),
    path('export-request-report/', export_request_report, name='export_request_report'),
    path('inventory-report/', inventory_report, name='inventory_report'),
    path('user-report/', user_item_request_report, name='user_report'),

    # Maintenance
    path('item-maintenance/', item_maintenance, name='item_maintenance'),
    path('user-item-maintenance/', user_item_maintenance, name='user_item_maintenance'),
    path('mark-maintained/<int:item_id>/', mark_maintained, name='mark_maintained'),
]
