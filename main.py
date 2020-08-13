import json
import argparse
import requests
from datetime import datetime
from datetime import timedelta


class BasicFit:

    # Authentication
    username = ""
    password = ""
    user = None

    # Session
    session = None

    # Clubs
    club = None
    clubs = []

    # Times
    times = []
    reserve_at = None

    # Urls
    login_url = "https://my.basic-fit.com/authentication/login"
    clubs_url = "https://my.basic-fit.com/door-policy/get-clubs"
    times_url = "https://my.basic-fit.com/door-policy/get-availability"
    book_url = "https://my.basic-fit.com/door-policy/book-door-policy"

    def __init__(self, username, password):
        #  Add arguments
        self.username = username
        self.password = password
        # Creates a new basic sessionsem
        self.create_new_session()
        # Get user credentials
        self.ask_for_credentials()
        # Auth
        logged_in = self.login()
        #
        if logged_in:
            # Steps required before reservation
            self.get_clubs()  # Get all clubs from basic
            # Make the actual reservation
            self.make_reservation()
        else:
            print("Error")

    def make_reservation(self):
        """ Make reservation interactive """
        print("Hi " + self.user["member"]["first_name"])
        # Ask for the club
        self.ask_for_club()
        # Get times for the club
        self.get_times()
        # Ask for the time
        self.ask_for_time()
        #
        self.post_reservation()

    def ask_for_time(self):
        raw_time = input("At what time? (hh:mm): ")
        for time in self.times:
            # Check if name contains
            if time["startDateTime"][-8:-3] == raw_time and time["openForReservation"]:
                # Timeslot is open
                self.reserve_at = time
                return True
        # Not available
        return False

    def ask_for_club(self):
        """ Asks the user what gym to reserve """
        raw_club = input("Which gym would you like?: ")
        # Make list for all possible clubs
        possible = []
        # Do loop
        for club in self.clubs:
            # Check if name contains
            if raw_club in club["name"].lower():
                possible.append(club)
        # Check if club found
        if len(possible) == 0:
            print("Nothing found...")
            return self.ask_for_club()
        elif len(possible) == 1:
            self.club = possible[0]
        else:
            # Nice index for user
            index = 1
            # Display everything
            for option in possible:
                print("#" + str(index) + " - " + option["name"])
                index += 1
            # Ask user
            raw_index = input("#: ")
            # store
            self.club = possible[int(raw_index) - 1]

    def create_new_session(self):
        """ Creates a new session """
        self.session = requests.Session()
        # Add required headers
        self.session.headers.update({'Accept': 'application/json'})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.session.headers.update({'mbf-rct-app-api-2-caller': 'true'})
        self.session.headers.update({'mbfLoginHeadVForm': 'jk#Bea201'})

    def ask_for_credentials(self):
        """ Asks the user to enter credentials """
        if not self.username:
            self.username = input("Username: ")
        if not self.password:
            self.password = input("Password: ")

    def create_login_request_body(self):
        """ Creates a body for the login request """
        return json.dumps({
            "email": self.username,
            "password": self.password,
            "cardNumber": ""
        })

    def login(self):
        """ Handles the actual login request """
        res = self.session.post(self.login_url, self.create_login_request_body())
        # Check for status
        if res.status_code == 200:
            # Store User
            self.user = res.json()
            return True
        else:
            print(res.content)
            return False

    def get_clubs(self):
        """ Get all of the clubs of Basic Fit """
        req = self.session.get(self.clubs_url)
        # Check for status
        if req.status_code == 200:
            self.clubs = req.json()
            return True
        else:
            return False

    def create_times_request_body(self):
        """ Creates a body for the login request """
        return json.dumps({
            "clubId": self.club["id"],
            "dateTime": (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        })

    def get_times(self):
        """ Get all of the clubs of Basic Fit """
        req = self.session.post(self.times_url, self.create_times_request_body())
        # Check for status
        if req.status_code == 200:
            self.times = req.json()
            return True
        else:
            return False

    def create_reservation_request_body(self):
        """ Creates a body for the login request """
        return json.dumps({
            "clubOfChoice": self.club,
            "doorPolicy": self.reserve_at,
            "duration": 120
        })

    def post_reservation(self):
        """ Do actual reservation """
        res = self.session.post(self.book_url, self.create_reservation_request_body())

        print(res.content)

def main():
    """ Shorcut for passing username and password """
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('-u', dest="username")
    parser.add_argument('-p', dest="password")
    # Parse
    args = parser.parse_args()
    # New Basic Instance
    BasicFit(args.username, args.password)


main()
