from datetime import datetime
import os
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import forecast_usage_from_excel, is_clerk, is_hod, is_faculty  # Assuming this is defined in a utils.py file in the same app

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
