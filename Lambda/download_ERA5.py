from io import BytesIO
import json
import boto3
from botocore.exceptions import ClientError

import urllib3
import cdsapi

def external_api_call(year, month, day):
    secret_name = "dev/reanalysis"
    region_name = "sa-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response['SecretString'])
    # API Call
    cdsapi_client = cdsapi.Client(url='https://cds.climate.copernicus.eu/api/v2',key=secret['key'])
    results = cdsapi_client.retrieve(
    'reanalysis-era5-land',
    {
        'variable': [
            '2m_temperature', 'total_precipitation',
        ],
        'year': year,
        'month': month,
        'day': day,
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'area': [
            -9, -60, -24,
            -40,
        ],
        'format': 'netcdf',
    }, None)
    return results

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    year = event.get('year', None)
    month = event.get('month',None)
    day = event.get('day',None)
    
    if year is None or month is None or day is None:
        return {
            'message' : f'Missing required argument. One of "year", "month", "day".' 
        }
    
    # Call external API
    api_call_results = external_api_call(year=year,month=month,day=day)
    url = api_call_results.location
    length = api_call_results.content_length
     
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    image_data = BytesIO(r.data)
    bucket_name = 'picsel-demo-input'
    image_data.seek(0)
    
    target_location = f'data/era5land_{year}-{month}-{day}.nc'
    
    s3.upload_fileobj(image_data, bucket_name, target_location)
    return { 
        'message' : f'File of length {length} located at {url} downloaded successfully and saved to {target_location}.' 
    }
