import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
def is_clerk(user):
    return user.groups.filter(name='Clerk').exists()

def is_faculty(user):
    return user.groups.filter(name='Faculty').exists()

def is_hod(user):
    return user.groups.filter(name='HOD').exists()

def forecast_usage_from_excel(file_path, forecast_year):
    df = pd.read_excel(file_path)

    last_year = df.columns[-1]
    if isinstance(last_year, str):
        last_year = int(last_year)
    steps_ahead = forecast_year - last_year

    if steps_ahead <= 0:
        raise ValueError("Forecast year must be greater than the last year in the dataset!")

    hw_predictions = {}

    for row in df.itertuples(index=False):
        item_name = row.Item
        usage_values = list(row[1:])
        year_range = list(range(2020, 2020 + len(usage_values)))
        usage_series = pd.Series(usage_values, index=year_range)

        model = ExponentialSmoothing(usage_series, trend='add', seasonal=None)
        fit = model.fit()

        prediction = fit.forecast(steps_ahead).iloc[-1]
        hw_predictions[item_name] = int(prediction) + 1

    return hw_predictions
