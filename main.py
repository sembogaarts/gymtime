import argparse
import time
from datetime import datetime
from getpass import getpass
from api import basic_fit_api


class BasicFit:
    # User information
    user = None
    open_reservations = 0
    reservation = None
    session = None
    availability = []
    date_for_booking = None

    # Constants
    max_gym_duration = 90
    max_open_reservations = 2

    def __init__(self, email, password, book_at_date, book_at_time, interval):
        #  Add arguments from CLI
        self.email = email
        self.password = password
        self.book_at_time = book_at_time
        self.book_at_date = book_at_date
        self.interval = interval or 30
        # If the user didn't pass the credentials via the CLI
        self.ask_for_credentials_if_missing()
        # Create a new session for the user
        self.session = self.login()
        # Create a reservation
        self.reservation = self.start_new_booking()
        # Finished! Wrap everything up
        self.inform_about_reservation()

    def start_new_booking(self):
        try:
            # Get user information for a personalised CLI experience
            self.user = basic_fit_api.get_member_information(self.session)
            # Get the amount of open reservations
            self.open_reservations = basic_fit_api.get_open_reservations_count(self.session)
            # Check if it's possible to reserve more
            if self.open_reservations >= self.max_open_reservations:
                raise Exception("Maximum amount of bookings already")
            # Give the user feedback that everything is OK
            self.say_hi()
            self.ask_for_date()
            # Lets the to book
            self.try_to_make_reservation()
        except Exception as error:
            print(error)
            self.credits()
            exit()

    def say_hi(self):
        """ Give a little love to the member """
        print("Hi {}, I selected {} as your gym, you have {} open booking(s).".format(
            self.user["first_name"],
            self.user["favorite_club"]["name"],
            self.open_reservations)
        )

    def ask_for_date(self):
        """ Let's determine the date the member want to gym at """
        if not self.book_at_date:
            print("What date would you like me to book? (blank for today)")
            self.book_at_date = input("[{}]: ".format(datetime.today().strftime('%d-%m-%Y')))
        if not self.book_at_time:
            print("What time would you like me to book?")
            self.book_at_time = input("[hh:mm]: ")
        # Parse the time
        self.parse_time_for_booking()

    def parse_time_for_booking(self):
        """  Try to parse the date to a workable format """
        try:
            # Defaults to today if blank
            if not self.book_at_date:
                self.book_at_date = datetime.today().strftime('%d-%m-%Y')
            # Concat the date with the time
            date_string = "{} {}".format(self.book_at_date, self.book_at_time)
            # Parse the date string to a workable format
            self.date_for_booking = datetime.strptime(date_string, '%d-%m-%Y %H:%M')
        except:
            print("Time format is invalid, use something like: 10:00 or 11:45")
            self.book_at_time = None  # Clear the invalid time
            self.book_at_date = None  # Clear the invalid date
            self.ask_for_date()  # Ask again

    def try_to_make_reservation(self):
        """ Checks if there's a session available for the date """
        # Fetch the availability for favourite gym
        self.availability = basic_fit_api.get_available_times_for_members_favourite_club(
            self.session,
            self.user,
            self.date_for_booking
        )
        # Quick check for availability
        if len(self.availability) == 0:
            raise Exception("There are no more sessions available on this date")
        # Check all policy's
        for policy in self.availability:
            # Parse the date string to a workable format
            session_date = datetime.strptime(policy['startDateTime'], '%Y-%m-%dT%H:%M:%S.%f')
            # Check for the specific time
            if session_date.time() == self.date_for_booking.time():
                # Create the reservation
                return basic_fit_api.create_reservation(
                    self.session,
                    self.user["favorite_club"],
                    policy,
                    self.max_gym_duration
                )
        # Preferred time is unavailable
        self.retry_to_book_preferred_time()

    def retry_to_book_preferred_time(self):
        """ Fully booked at specified time """
        print("{} seems to be fully booked at {}".format(self.user['favorite_club']['name'], self.book_at_time))
        time.sleep(self.interval)
        self.try_to_make_reservation()

    def ask_for_credentials_if_missing(self):
        """ Asks the user to enter credentials """
        if not self.email:
            self.email = input("Email: ")
        if not self.password:
            self.password = getpass()

    def login(self):
        """ Creates a new session """
        try:
            # Try to get the JWT token from Basic Fit
            jwt_token = basic_fit_api.get_jwt_from_credentials(self.email, self.password)
            # Exchange JWT token for Cookie
            return basic_fit_api.exchange_jwt_for_session(jwt_token)
        except Exception as error:
            exit(error)

    def inform_about_reservation(self):
        print(
            "Your reservation for {} at {} is confirmed! You'll receive an email from Basic-Fit any second.".format(
                self.date_for_booking.strftime('%d-%m-%Y %H:%M'),
                self.user['favorite_club']['name']
            )
        )
        self.credits()

    def credits(self):
        print("---")
        print("Issues, new ideas and stars are welcome!")
        print("https://github.com/sembogaarts/gymtime")


def main():
    """ Shorcut for passing email and password """
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('-u', dest="email", help="E-mail used for your Basic-Fit account")
    parser.add_argument('-p', dest="password", help="Password used for your Basic-Fit account")
    parser.add_argument('-d', dest="date", help="Date for the reservations (dd-mm-yyyy)")
    parser.add_argument('-t', dest="time", help="Time for the reservations (hh:mm)")
    parser.add_argument('-i', dest="interval", help="Interval in seconds before retrying again", default="30")
    # Parse
    args = parser.parse_args()
    # New Basic Instance
    BasicFit(
        args.email,
        args.password,
        args.date,
        args.time,
        args.interval
    )


main()
