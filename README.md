`pip install -r requirements.txt`

At the moment openmeteo_sdk doesn't install correctly  
`wget https://github.com/open-meteo/sdk/archive/refs/tags/v1.10.0.tar.gz -O 'openmeteo-sdk-1.10.0.tar.gz'`
`tar zxvf openmeteo-sdk-1.10.0.tar.gz`
`sudo cp -R sdk-1.10.0/python/openmeteo_sdk/  /home/pi/.local/lib/python3.9/site-packages`

Amount of days. It shows the weather starting with today's day at midnight.
`python3 weather3.py 2`
