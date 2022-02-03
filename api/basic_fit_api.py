import requests
from json import dumps

def get_jwt_from_credentials(email, password):
    """ Exchanges the user credentials to a JWT token """
    body = dumps({
        "email": email,
        "password": password
    })

    headers = {
        'Host': 'bfa-login.basic-fit.com',
        'content-type': 'application/json',
        'accept': 'application/json',
        'user-agent': 'Basic Fit App/1.3.1.0 (iOS)',
        'accept-language': 'en-GB,en;q=0.9',
    }

    response = requests.post("https://bfa-login.basic-fit.com/login", data=body, headers=headers)

    if response.status_code != 200:
        raise Exception("Unable to authenticate at Basic-Fit")

    auth = response.json()

    if "accessToken" not in auth:
        raise Exception("Unable to get JWT from Basic-Fit")

    return auth["accessToken"]

def exchange_jwt_for_session(jwt_token):
    """ Exhanges the JWT token for a SID cookie """
    session = requests.session()

    endpoint = "https://my.basic-fit.com/sso?token={}&returl=https://my.basic-fit.com/gym-time-booking&langCountry=nl-nl".format(
        jwt_token)

    session.headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': 'bearer {}'.format(jwt_token),
        'accept-language': 'en-gb',
        'Accept-Encoding': 'gzip, deflate, br',
        'authority': 'my.basic-fit.com',
        'Host': 'my.basic-fit.com',
        'origin': 'https://my.basic-fit.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.1',
        'Referer': endpoint,
        'Connection': 'keep-alive',
        'mbfLoginHeadVForm': 'jk#Bea201',
        'mbf-rct-app-api-2-caller': 'true',
        'content-type': 'application/json'
    }

    response = session.post("https://my.basic-fit.com/sso", data={})

    if response.status_code != 200:
        raise Exception("Can't exchange JWT for SID cookie")

    return session

def get_member_information(session):
    """ Get all the information about the member """
    response = session.get("https://my.basic-fit.com/member/get-member")

    if response.status_code != 200:
        raise Exception("Can't fetch information about member")

    return response.json()

def get_open_reservations_count(session):
    """ Get open reservations for the member """
    response = session.get("https://my.basic-fit.com/door-policy/get-open-reservation")

    if response.status_code != 200:
        raise Exception("Can't fetch reservations for member")

    return len(response.json()["data"])

def get_available_times_for_members_favourite_club(session, user, date):
    """ Get all the available times for the club """
    body = dumps({
        "clubId": user["favorite_club"]["id"],
        "dateTime": date.strftime('%Y-%m-%d')
    })

    response = session.post("https://my.basic-fit.com/door-policy/get-availability", data=body)

    if response.status_code != 200:
        raise Exception("Can't fetch availability for members favourite gym")

    return response.json()

def create_reservation(session, club, policy, duration):
    """ Creates a body for the login request """
    body = dumps({
        "clubOfChoice": club,
        "doorPolicy": policy,
        "duration": duration
    })

    response = session.post("https://my.basic-fit.com/door-policy/book-door-policy", data=body)

    if response.status_code != 200:
        raise Exception("Can't book the policy at the club")

    return response.json()