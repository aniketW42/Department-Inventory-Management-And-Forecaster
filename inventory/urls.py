from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    # path('request-item/<int:item_id>/', request_item, name='request_item'),

    path('faculty-dashboard/', faculty_dashboard, name='faculty_dashboard'),
    path('clerk-dashboard/', clerk_dashboard, name='clerk_dashboard'),
    path('hod-dashboard/', hod_dashboard, name='hod_dashboard'),
    path('logout/', logout_page, name='logout'),
    path('login/', login_page, name='login'),
    path('manage-requests/', manage_requests, name='manage_requests'),
    path('process-request/<int:request_id>/', process_request, name='process_request'),
    path('view-all-requests/', view_all_requests, name='view_all_requests'),
    path('view_requests/<int:user_id>', view_requests, name='view_requests' ),
    path('request-history/', request_history, name='request_history'),
    path('issue-items/', issue_items, name='issue_items'),
    path('issue-items/<int:request_id>/mark/', mark_as_issued, name='mark_as_issued'),
    path('inventory-items', show_all_items, name='inventory_items'),
    path('items/add/', add_item, name='add_item'),
    path('items/edit/<int:pk>/', edit_item, name='edit_item'),
    path('delete-item/<int:pk>/', delete_item, name='delete_item'),
    path('predict-usage/<int:year>', predict_usage, name='predict_usage'),
    path('request-item/', request_item_page, name='request_item'),
    path('submit-request/', submit_item_request, name='request_item_submit'),
    # path('categories/', category_list, name='category_list'),
    path('forecast/', inventory_forecast_view, name='inventory_forecast'),
    path('create-user/', create_user, name='create_user'),
    path('manage-users/', manage_users, name='manage_users'),
    path('reports/', reports, name='reports'),
    path('item-request-report/', item_request_report, name='item_request_report'),
    path('export-request-report/', export_request_report, name='export_request_report'),
    path('item-maintenance/', item_maintenance, name='item_maintenance'),
    

]
