import requests
import datetime
import time
import os
from lxml import html

USERNAME = os.environ['COMPOST_NOW_USER']
PASSWORD = os.environ['COMPOST_NOW_PASS']

LOGIN_URL = "https://compostnow.org/member/login/?next=/member/"
MEMBER_URL = "https://compostnow.org/member/"
SKIP_URL = "https://compostnow.org/member/ajax/skip"

def main():
    session_requests = requests.session()

    # Get login csrf token
    result_login_get = session_requests.get(LOGIN_URL)
    csrfmiddlewaretoken = list(set(html.fromstring(result_login_get.text).xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

    # Create login payload
    login_payload = {
        "username": USERNAME, 
        "password": PASSWORD, 
        "csrfmiddlewaretoken": csrfmiddlewaretoken
    }

    # Perform login
    result_login_post = session_requests.post(LOGIN_URL, data = login_payload, headers = dict(referer = LOGIN_URL))

    # Get member page for a fresh csrf middleware token & service pickup day
    result_member_page_get = session_requests.get(MEMBER_URL, headers = dict(referer = MEMBER_URL))
    pickup_day_str = html.fromstring(result_member_page_get.text).xpath("//div[@id='service_day']//p//strong/text()")[0].strip()
    pickup_day_int = time.strptime(pickup_day_str, "%A").tm_wday
    today = datetime.date.today()
    
    # Calculate next pickup date from pickup day
    next_pickup = today + datetime.timedelta( (pickup_day_int-today.weekday()) % 7 )
    csrfmiddlewaretoken = list(set(html.fromstring(result_member_page_get.text).xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

    # Slokip Payad
    skip_payload = {
        "skip_dates": next_pickup,
        "csrfmiddlewaretoken": csrfmiddlewaretoken
    }

    # Send POST to skip next pickup
    result_skip_post = session_requests.post(SKIP_URL, data = skip_payload, headers = dict(referer = MEMBER_URL))
    print(result_skip_post.text)

if __name__ == '__main__':
    main()