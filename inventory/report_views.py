
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from .models import ItemRequest, InventoryItem
import calendar
import csv

@login_required
def item_request_report(request):
    report_type = request.GET.get('report_type', 'monthly')
    year = request.GET.get('year')
    month = request.GET.get('month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    item = request.GET.get('item')
    status = request.GET.get('status')
    user = request.GET.get('user')

    queryset = ItemRequest.objects.none()
    selected_period = ""

    # Report type logic
    if report_type == 'yearly' and year:
        queryset = ItemRequest.objects.filter(request_date__year=year).order_by('request_date')
        selected_period = f"Year {year}"

    elif report_type == 'monthly' and month:
        try:
            year_val, month_val = map(int, month.split('-'))
            queryset = ItemRequest.objects.filter(request_date__year=year_val, request_date__month=month_val).order_by('request_date')
            selected_period = f"{calendar.month_name[month_val]} {year_val}"
        except Exception:
            selected_period = "Invalid month"

    elif report_type == 'custom' and start_date and end_date:
        try:
            start = parse_date(start_date)
            end = parse_date(end_date)
            if start and end:
                queryset = ItemRequest.objects.filter(request_date__range=(start, end)).order_by('request_date')
                selected_period = f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}"
        except Exception:
            selected_period = "Invalid custom range"
    # print(selected_period)
    # Apply filters
    if item:
        queryset = queryset.filter(item__name__icontains=item).order_by('request_date')
    if status:
        queryset = queryset.filter(status=status).order_by('request_date')
    if user:
        queryset = queryset.filter(user__username__icontains=user).order_by('request_date')

    status_choices = ['pending', 'approved', 'rejected', 'issued', 'returned']

    return render(request, 'reports/item_request_report.html', {
        'requests': queryset,
        'selected_period': selected_period,
        'status_choices': status_choices,
    })


@login_required
def export_request_report(request):
    format = request.GET.get('format', 'csv')
    month = request.GET.get('month')
    item = request.GET.get('item')
    status = request.GET.get('status')
    user = request.GET.get('user')

    year, month_number = map(int, month.split('-'))
    queryset = ItemRequest.objects.filter(
        request_date__year=year,
        request_date__month=month_number
    )

    if item:
        queryset = queryset.filter(item__name__icontains=item)
    if status:
        queryset = queryset.filter(status=status)
    if user:
        queryset = queryset.filter(user__username__icontains=user)

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="item_request_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Item', 'User', 'Quantity', 'Status', 'Request Date'])

        for req in queryset:
            writer.writerow([
                req.item.name,
                req.user.username,
                req.quantity,
                req.status,
                req.request_date.strftime("%Y-%m-%d %H:%M")
            ])
        return response

    # Future: handle PDF here

    return HttpResponse("Invalid format", status=400)


@login_required
def reports(request):
    approved_count = ItemRequest.objects.filter(status='approved').count()
    pending_count = ItemRequest.objects.filter(status='pending').count()
    rejected_count = ItemRequest.objects.filter(status='rejected').count()
    issued_count = ItemRequest.objects.filter(status='issued').count()
    returned_count = ItemRequest.objects.filter(status='returned').count()

    in_stock_count = InventoryItem.objects.filter(quantity__gt=10).count()
    low_stock_count = InventoryItem.objects.filter(quantity__gt=0, quantity__lte=10).count()
    out_of_stock_count = InventoryItem.objects.filter(quantity=0).count()

    context = {
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'issued_count' : issued_count,
        'returned_count': returned_count,
        'in_stock_count': in_stock_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }

    return render(request, 'reports/reports.html', context)


def inventory_report(request):
    report_type = request.GET.get('report_type', 'monthly')
    year = request.GET.get('year')
    month = request.GET.get('month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    item = request.GET.get('item')

    queryset = InventoryItem.objects.all()
    selected_period = ""

    try:
        if report_type == 'yearly' and year:
            year_int = int(year)
            queryset = queryset.filter(date_added__year=year_int)
            selected_period = f"Year {year_int}"
        elif report_type == 'monthly' and month:
            # Expecting month param in 'YYYY-MM' format
            year_val, month_val = map(int, month.split('-'))
            queryset = queryset.filter(date_added__year=year_val, date_added__month=month_val)
            selected_period = f"{calendar.month_name[month_val]} {year_val}"
        elif report_type == 'custom' and start_date and end_date:
            start = parse_date(start_date)
            end = parse_date(end_date)
            if start and end:
                queryset = queryset.filter(date_added__date__range=(start, end))
                selected_period = f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}"
            else:
                selected_period = "Invalid date range"
        else:
            # No valid filter - maybe show all or show message
            selected_period = "All time"
    except Exception as e:
        selected_period = f"Invalid filter parameters: {e}"

    if item:
        queryset = queryset.filter(name__icontains=item)

    if request.GET.get('export') == 'excel':
        return export_inventory_to_excel(queryset, selected_period)


    return render(request, 'reports/inventory_report.html', {
        'items': queryset,
        'selected_period': selected_period,
    })

import io
import datetime
from django.http import HttpResponse
import openpyxl
from openpyxl.utils import get_column_letter

def export_inventory_to_excel(queryset, selected_period):
    # Create a workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventory Report"

    # Header row
    headers = ['#', 'Item', 'Category', 'Quantity', 'Location', 'Date Added']
    ws.append(headers)

    # Fill rows
    for idx, item in enumerate(queryset, start=1):
        ws.append([
            idx,
            item.name,
            item.get_category_display() if hasattr(item, 'get_category_display') else item.category,
            item.quantity,
            item.location,
            item.date_added.strftime('%Y-%m-%d'),
        ])

    # Set column widths for readability
    for i, column_cells in enumerate(ws.columns, start=1):
        max_length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[get_column_letter(i)].width = max_length + 2

    # Save workbook to in-memory file
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Create response
    filename = f"inventory_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
