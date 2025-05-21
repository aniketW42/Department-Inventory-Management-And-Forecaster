from datetime import datetime
import os
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from .utils import forecast_usage_from_excel, is_clerk, is_hod, is_faculty  # Assuming this is defined in a utils.py file in the same app
from inventory.models import ItemRequest, InventoryItem  # Importing the ItemRequest and InventoryItem models

def inventory_forecast_view(request):
    forecast_results = None
    forecast_year = [ datetime.now().year + 1, datetime.now().year + 2 ]  # Default to next year
    year = datetime.now().year + 1  
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        year = request.POST.get('forecast_year')
        if uploaded_file.name.endswith('.xlsx'):
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            try:
                
                forecast_results = forecast_usage_from_excel(file_path, int(year))

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
            finally:
                os.remove(file_path)
        else:
            messages.error(request, "Please upload a .xlsx file only.")

    return render(request, 'forecast/forecast_page.html', {
        'forecast_data': forecast_results,
        'forecast_year': forecast_year,
        'selected_year': year
    })


@login_required
@user_passes_test(is_clerk or is_hod)
def predict_usage(request, year):
    forecast_data = {}
    try:
        year = int(year)
    except ValueError:
        return JsonResponse({'error': 'Invalid year format'}, status=400)
    forecast_year = year 

    excel_path = os.path.join('media', 'stationery_usage.xlsx') 
    try:
        forecast_data = forecast_usage_from_excel(excel_path, forecast_year)
    except Exception as e:
        forecast_data = {'error': str(e)}

    return render(request, 'predict_usage.html', {
        'forecast_data': forecast_data,
        'forecast_year': forecast_year
    })

# import pandas as pd
# from statsmodels.tsa.holtwinters import ExponentialSmoothing
# from django.shortcuts import render
# from inventory.models import InventoryItem, ItemRequest
# from datetime import datetime

# def forecast_inventory_usage(request, forecast_years=1):
#     # Fetch issued requests only for consumable items
#     issued_requests = ItemRequest.objects.filter(status='issued', item__item_type='consumable').order_by('request_date')
#     if not issued_requests.exists():
#         return render(request, 'predict_usage2.html', {
#             'error': 'No issued item requests found in the database.',
#             'forecast_data': {},
#             'past_usage': {},
#             'forecast_year': forecast_years,
#             'years_to_show': []
#         })

#     current_year = datetime.now().year
#     years_to_show = list(range(current_year - 4, current_year))  # Last 4 years (exclude current year)

#     items = InventoryItem.objects.filter(item_type='consumable')
#     usage_data = {item.name: {year: 0 for year in years_to_show} for item in items}

#     # Aggregate issued quantity per year per item
#     for item in items:
#         item_requests = issued_requests.filter(item=item)
#         for req in item_requests:
#             year = req.request_date.year
#             if year in usage_data[item.name]:
#                 usage_data[item.name][year] += req.quantity

#     forecast_result = {}
#     for item_name, yearly_data in usage_data.items():
#         sorted_years = sorted(yearly_data.keys())
#         values = [yearly_data[year] for year in sorted_years]

#         # Create a PeriodIndex with yearly frequency for the series index
#         idx = pd.PeriodIndex(sorted_years, freq='Y')
#         series = pd.Series(values, index=idx)

#         if series.sum() == 0 or series.count() < 3:
#             forecast_result[item_name] = "Not enough data"
#             continue

#         try:
#             model = ExponentialSmoothing(series, trend='add', seasonal=None)
#             fit = model.fit()
#             forecast = fit.forecast(forecast_years)

#             # Convert forecast PeriodIndex to string year for template
#             forecast_result[item_name] = {
#                 str(period.year): int(round(forecast_val)) for period, forecast_val in forecast.items()
#             }
#         except Exception as e:
#             forecast_result[item_name] = f"Forecasting error: {str(e)}"

#     return render(request, 'predict_usage2.html', {
#         'forecast_data': forecast_result,
#         'past_usage': usage_data,
#         'forecast_year': forecast_years,
#         'years_to_show': years_to_show,
#     })

import pandas as pd

def forecast_inventory_usage(request, forecast_years=1):
    issued_requests = ItemRequest.objects.filter(status='issued', item__item_type='consumable').order_by('request_date')
    if not issued_requests.exists():
        return render(request, 'predict_usage2.html', {
            'error': 'No issued item requests found in the database.',
            'forecast_data': {},
            'past_usage': {},
            'current_stock': {},
            'need_to_order': {},
            'forecast_year': forecast_years,
            'years_to_show': []
        })

    current_year = datetime.now().year
    years_to_show = list(range(current_year - 4, current_year))  # Last 4 years excluding current

    items = InventoryItem.objects.filter(item_type='consumable')
    usage_data = {item.name: {year: 0 for year in years_to_show} for item in items}
    current_stock = {item.name: item.quantity for item in items}  # Current available quantity

    for item in items:
        item_requests = issued_requests.filter(item=item)
        for req in item_requests:
            year = req.request_date.year
            if year in usage_data[item.name]:
                usage_data[item.name][year] += req.quantity

    forecast_result = {}
    need_to_order = {}

    for item_name, yearly_data in usage_data.items():
        sorted_years = sorted(yearly_data.keys())
        values = [yearly_data[year] for year in sorted_years]

        idx = pd.PeriodIndex(sorted_years, freq='Y')
        series = pd.Series(values, index=idx)

        if series.sum() == 0 or series.count() < 3:
            forecast_result[item_name] = "Not enough data"
            need_to_order[item_name] = "-"
            continue

        try:
            model = ExponentialSmoothing(series, trend='add', seasonal=None)
            fit = model.fit()
            forecast = fit.forecast(forecast_years)

            forecast_year_values = {str(period.year): int(round(forecast_val)) for period, forecast_val in forecast.items()}
            forecast_result[item_name] = forecast_year_values

            # Calculate need to order for first forecast year only (you can adjust logic for multiple years if needed)
            first_forecast_year = list(forecast_year_values.keys())[0]
            forecast_qty = forecast_year_values[first_forecast_year]
            available_qty = current_stock.get(item_name, 0)
            need_qty = forecast_qty - available_qty
            need_to_order[item_name] = need_qty if need_qty > 0 else 0

        except Exception as e:
            forecast_result[item_name] = f"Forecasting error: {str(e)}"
            need_to_order[item_name] = "-"

    forecast_years_used = sorted(list(forecast_year_values.keys()))

    return render(request, 'predict_usage2.html', {
        'forecast_data': forecast_result,
        'past_usage': usage_data,
        'current_stock': current_stock,
        'need_to_order': need_to_order,
        'forecast_year': forecast_years,
        'years_to_show': years_to_show,
        'forecast_years_used': forecast_years_used, 
    })
