import urequests
import ujson

### FIRST WLAN CONNECTION MUST BE CREATED BY RUNNING THE CODE IN ASSIGNMENT 5 ("WLAN+IP.py") ###

url = 'http://192.168.106.248:8000/' # example URL
response = urequests.get(url)
content = response.text


print(content)