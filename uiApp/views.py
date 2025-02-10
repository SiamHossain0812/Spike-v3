from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.core.files.storage import FileSystemStorage
from .models import SpikeData
import openpyxl
import csv
from datetime import datetime
from dateutil import parser  # Automatically detects date format


def get_station_range(station_id):
    """Fetch the highest and lowest values from the station_historical_data table."""
    try:
        print(f"Fetching range for station: {station_id}")
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT Recorded_Highest_WL, Recorded_Lowest_WL FROM station_historical_data WHERE STATION_ID = %s""",
                [station_id]
            )
            result = cursor.fetchone()
            if result:
                highest, lowest = result
                print(f"Found range for station {station_id}: Highest: {highest}, Lowest: {lowest}")
                return highest, lowest
    except Exception as e:
        print(f"Error fetching range for station {station_id}: {e}")
    return None, None


def store_uploaded_file(file_path, station_id):
    """Store the uploaded file data into the SpikeData model before processing."""
    print(f"Storing uploaded file data for station {station_id}. File: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Delete existing data for the station
            SpikeData.objects.all().delete()

            entries = []
            for row in reader:
                try:
                    # Automatically detect datetime format
                    dateTime_obj = parser.parse(row['dateTime'])

                    value_str = row['value'].strip()
                    value = None if value_str == '' else float(value_str)

                    # Store in model
                    entries.append(
                        SpikeData(
                            dateTime=dateTime_obj.strftime('%Y-%m-%d %H:%M:%S'),
                            value=value,
                            spike_value=None
                        )
                    )

                except Exception as e:
                    print(f"Skipping invalid row {row}: {e}")
            
            # Bulk insert all valid entries
            SpikeData.objects.bulk_create(entries)
            print(f"Stored {len(entries)} rows in the database.")

            return True, None

    except Exception as e:
        print(f"Error storing uploaded file: {e}")
        return False, "Error storing uploaded file."


def process_spike_detection(station_id):
    """Process spike detection for the uploaded data in the SpikeData model."""
    print(f"Processing spike detection for station {station_id}")

    highest, lowest = get_station_range(station_id)
    if highest is None or lowest is None:
        return "Station ID not found in historical data.", 0

    previous_valid_values = []  # Store last valid values while skipping NULLs
    spike_count = 0  # Count spike values

    # Fetch all data sorted by dateTime
    data = SpikeData.objects.all().order_by('dateTime')

    for entry in data:
        value = entry.value
        spike_value = None

        if value is not None:
            # Check if the value is within the station's range
            if value < lowest or value > highest:
                spike_value, value = value, None  # Move out-of-range value to spike column
                spike_count += 1  # Increment spike count

            # **Ensure we correctly get the last 3 valid (non-null, non-spike) values**
            valid_previous_values = [v for v in previous_valid_values if v is not None]

            # **Look further back if fewer than 3 valid values exist (excluding spike values)**
            i = len(previous_valid_values) - 1
            while len(valid_previous_values) < 3 and i >= 0:
                if previous_valid_values[i] is not None:  # **Fixed condition**
                    valid_previous_values.insert(0, previous_valid_values[i])  # Add older valid values
                i -= 1

            if value is not None and len(valid_previous_values) >= 3:
                last_three_values = valid_previous_values[-3:]  # Always take the last 3 valid values
                differences = [abs(value - prev) for prev in last_three_values]

                if any(diff >= 1 for diff in differences):
                    spike_value, value = value, None  # Move to spike_value column
                    spike_count += 1  # Increment spike count
                    print(f"Spike detected at {entry.dateTime}: Value = {spike_value}, Replacing with NULL")
                    print(f"Previous 3 valid values used for comparison (excluding spike values): {last_three_values}")

        # Store updated values in database
        entry.value = value
        entry.spike_value = spike_value
        entry.save()

        # **Maintain last valid values correctly, ensuring only last 3 are kept**
        if value is not None:
            previous_valid_values.append(value)  # Only store non-null, non-spike values

        # **Fix: Keep only the last 3 valid values for further comparisons**
        previous_valid_values = [v for v in previous_valid_values if v is not None][-3:]

    print(f"Spike detection completed. Total spikes detected: {spike_count}")
    return None, spike_count




def spikedata(request):
    """Main view to handle file upload and processing."""
    print("Fetching station IDs...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT STATION_ID FROM station_historical_data")
            stations = [{'station_id': row[0]} for row in cursor.fetchall()]
    except Exception as e:
        return render(request, 'spikedata.html', {'error': f"Error fetching station IDs: {e}"})

    if request.method == 'POST' and 'file_upload' in request.FILES:
        print("Handling file upload...")
        file = request.FILES['file_upload']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        filepath = fs.path(filename)

        station_id = request.POST.get('station_name')
        print(f"Processing station {station_id}...")

        # Step 1: Store uploaded data in database
        success, error = store_uploaded_file(filepath, station_id)
        if not success:
            return render(request, 'spikedata.html', {'error': error, 'stations': stations})

        # Step 2: Process spike detection
        error, spike_count = process_spike_detection(station_id)
        if error:
            return render(request, 'spikedata.html', {'error': error, 'stations': stations})

        processed_data = list(SpikeData.objects.values('dateTime', 'value', 'spike_value'))
        request.session['processed_data'] = processed_data

        return render(request, 'spikedata.html', {
            'summary': {
                'total_data_points': len(processed_data),
                'last_uploaded_file_name': filename,
                'stored_station_name': station_id,
                'spike_count': spike_count  # Add spike count to summary
            },
            'stations': stations,
            'processed_data': processed_data
        })

    return render(request, 'spikedata.html', {'stations': stations})



def export_spikedata(request):
    """Export processed data as a CSV file."""
    processed_data = request.session.get('processed_data')
    if not processed_data:
        return HttpResponse("No processed data available for export.", status=400)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="processed_water_level_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['dateTime', 'value', 'spike_value'])
    for data in processed_data:
        writer.writerow([data['dateTime'], data['value'], data['spike_value']])

    return response




def upload_station_data(request):
    """Upload station historical data into station_historical_data table."""
    if request.method == 'POST' and request.FILES['excel_file']:
        file = request.FILES['excel_file']

        if not file.name.endswith(('.xlsx', '.xls', '.csv')):
            return render(request, 'upload_station_data.html', {'error': 'Invalid file format. Upload Excel or CSV only.'})

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        filepath = fs.path(filename)

        try:
            if filename.endswith('.csv'):
                with open(filepath, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        with connection.cursor() as cursor:
                            cursor.execute("INSERT INTO station_historical_data (STATION_ID, Recorded_Highest_WL, Recorded_Lowest_WL) VALUES (%s, %s, %s)", [row['STATION_ID'], row['Recorded_Highest_WL'], row['Recorded_Lowest_WL']])

            else:
                wb = openpyxl.load_workbook(filepath)
                sheet = wb.active
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO station_historical_data (STATION_ID, Recorded_Highest_WL, Recorded_Lowest_WL) VALUES (%s, %s, %s)", [row[0], row[1], row[2]])

            return render(request, 'upload_station_data.html', {'success': 'File uploaded successfully!'})

        except Exception as e:
            return render(request, 'upload_station_data.html', {'error': f'Error processing file: {str(e)}'})

    return render(request, 'upload_station_data.html')
