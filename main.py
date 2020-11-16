import json
import argparse
import requests
from datetime import datetime
from datetime import timedelta
import time


class BasicFit:
    # Authentication
    cookie = ""
    user = None

    # Prefered
    pref_club = None
    pref_time = None
    pref_hour = None
    pref_minutes = None
    pref_diff = None

    # Session
    session = None

    # Clubs
    club = None
    clubs = []

    # Times
    times = []
    reserve_at = None

    # Urls
    member_url = "https://my.basic-fit.com/member/get-member"
    clubs_url = "https://my.basic-fit.com/door-policy/get-clubs"
    times_url = "https://my.basic-fit.com/door-policy/get-availability"
    book_url = "https://my.basic-fit.com/door-policy/book-door-policy"
    open_reservation_url = "https://my.basic-fit.com/door-policy/get-open-reservation"

    def __init__(self, username, password, club, time):
        #  Add arguments
        self.username = username
        self.password = password
        # Prefered
        self.pref_club = club
        self.pref_time = time
        # Creates a new basic sessionsem
        self.create_new_session()
        # Get user credentials
        self.ask_for_credentials()
        # Auth
        self.get_member()
        #
        if not self.user:
            print("Unable to login at Basic-Fit")
            exit()
        # Check if the user can reserve
        can_reserve = not self.has_open_reservation()
        # Perform check
        if not can_reserve:
            print("You already have an open reservation")
            exit()
        # Steps required before reservation
        self.get_clubs()  # Get all clubs from basic
        # Make the actual reservation
        self.make_reservation()

    def make_reservation(self):
        """ Make reservation interactive """
        print("Hi " + self.user["first_name"])
        # Ask for the club
        self.ask_for_club()
        # Get times for the club
        self.get_times()
        # Ask for the time
        self.ask_for_time()
        #
        self.post_reservation()

    def ask_for_time(self):
        """ Asks the user for time """
        raw_time = self.pref_time if self.pref_time else input("At what time? [hh:mm]: ")
        # Parse time
        self.pref_hour = raw_time[0:2]
        self.pref_minutes = raw_time[3:5]
        self.pref_time = raw_time
        # Check if slot is available
        for time in self.times:
            # Check if name contains
            if time["startDateTime"][-8:-3] == raw_time and time["openForReservation"]:
                # Timeslot is open
                self.reserve_at = time
                return True
        # Not available
        return self.time_unavailable()

    def time_unavailable(self):
        #
        print("Timeslot is full, I will retry every 2 minutes.")

        self.pref_diff = int(input("How many slots?: "))

        if not self.pref_diff:
            self.pref_diff = 1
        else:

            parsed = datetime.strptime(self.pref_time, '%H:%M')

            diff = timedelta(minutes=self.pref_diff * 15)

            final = parsed - diff

            self.pref_time = '{}:{}'.format(final.hour, final.minute)

            self.pref_diff = (self.pref_diff * 2) + 1

        self.book_loop()

    def book_loop(self):

        self.get_times()

        for x in range(self.pref_diff):

            parsed = datetime.strptime(self.pref_time, '%H:%M')

            diff = timedelta(minutes=(15 * (x + 1)))

            final = parsed + diff

            timeslot = '{}:{}'.format(final.hour, str(final.minute).ljust(2, '0'))

            print('Trying: {}'.format(timeslot))

            for basicSlot in self.times:
                # Check if name contains
                if basicSlot["startDateTime"][-8:-3] == timeslot and basicSlot["openForReservation"]:
                    # Timeslot is open
                    self.reserve_at = basicSlot
                    return True

        time.sleep(30)

        self.book_loop()

    def ask_for_club(self):
        """ Asks the user what gym to reserve """
        raw_club = self.pref_club if self.pref_club else input("Which gym would you like?: ")
        # Make list for all possible clubs
        possible = []
        # Do loop
        for club in self.clubs:
            # Check if name contains
            if raw_club in club["name"].lower():
                possible.append(club)
        # Check if club found
        if len(possible) == 0:
            # Not available
            self.pref_time = None
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
        self.cookie = input("Cookie: ")
        self.session.headers.update({'cookie': self.cookie})

    def get_clubs(self):
        """ Get all of the clubs of Basic Fit """
        req = self.session.get(self.clubs_url)
        # Check for status
        if req.status_code == 200:
            self.clubs = req.json()
            return True
        else:
            return False

    def get_member(self):
        """ Get all of the clubs of Basic Fit """
        req = self.session.get(self.member_url)
        # Check for status
        if req.status_code == 200:
            self.user = req.json()
            return True
        else:
            return False

    def create_times_request_body(self):
        """ Creates a body for the login request """
        return json.dumps({
            "clubId": self.club["id"],
            "dateTime": datetime.today().strftime('%Y-%m-%d')
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
            "duration": 90
        })

    def post_reservation(self):
        """ Do actual reservation """
        res = self.session.post(self.book_url, self.create_reservation_request_body())

    def has_open_reservation(self):
        """ Check for open reservation """
        res = self.session.get(self.open_reservation_url)
        # Check if data isset
        if len(res.json()["data"]) > 0:
            return True
        else:
            return False


def main():
    """ Shorcut for passing username and password """
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('-u', dest="username")
    parser.add_argument('-p', dest="password")
    parser.add_argument('-c', dest="club")
    parser.add_argument('-t', dest="time")
    # Parse
    args = parser.parse_args()
    # New Basic Instance
    BasicFit(args.username,
             args.password,
             args.club,
             args.time)


main()
