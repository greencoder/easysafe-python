import requests
import json
import sys
import uuid
from optparse import OptionParser
import argparse

LOGIN_URL = 'https://simplisafe.com/mobile/login/'
LOGOUT_URL = 'https://simplisafe.com/mobile/logout'
LOCATIONS_URL = 'https://simplisafe.com/mobile/$UID$/locations'
DASHBOARD_URL = 'https://simplisafe.com/mobile/$UID$/sid/$LID$/dashboard'
EVENTS_URL = 'https://simplisafe.com/mobile/$UID$/sid/$LID$/events'
STATE_URL = 'https://simplisafe.com/mobile/$UID$/sid/$LID$/set-state'

class SimpliSafe():
    
    def __init__(self, debug=False):

        # Initialize variables
        self.session = None
        self.debug = False
        self.state = None
        self.uid = None
        self.location = None

        # Create a requests session to persist the cookies
        self.session = requests.session()

        # If we got debug passed, we'll print out diagnostics.
        if debug:
            self.debug = True

    def connect(self):
        self.login()
        self.get_location()
    
    def disconnect(self):
        self.logout()

    def abort(self, msg):
        print "Error: %s" % msg
        print "Aborting and Logging Out."
        self.logout()
        sys.exit()
            
    def set_state(self, state):
        
        if state not in ('home', 'away', 'off'):
            self.abort("State must be 'home', 'away', or 'off'. You tried '%s'." % state)
        
        state_data = {
            'state': state,
            'mobile': '1',
            'no_persist': '0',
            'XDEBUG_SESSION_START': 'session_name',
        }
        
        if self.debug:
            print "Setting System State To: %s" % state
        
        URL = STATE_URL.replace('$UID$', self.uid).replace('$LID$', self.location)
        response = self.session.post(URL, data=state_data)
        response_object = json.loads(response.text)
        
        if self.debug:
            print "Set State Response: %s" % response.text
        
        result_codes = {
            '2': 'off',
            '4': 'home',
            '5': 'away',
        }
        result_code = response_object['result']
        self.state = result_codes[str(result_code)]
        return result_codes[str(result_code)]

    def get_state(self):
        return self.state

    def get_temperature(self):
        return self.temperature

    def get_dashboard(self):
        
        if not self.uid:
            self.abort("You tried to get dashboard without first having a User ID set.")
        
        if not self.location:
            self.abort("You tried to get dashboard without first having a location set.")
        
        dashboard_data = {
            'no_persist': '0',
            'XDEBUG_SESSION_START': 'session_name',
        }
        
        URL = DASHBOARD_URL.replace('$UID$', self.uid).replace('$LID$', self.location)
        response = self.session.post(URL, data=dashboard_data)
        response_object = json.loads(response.text)
        
        if self.debug:
            print "Dashboard Response: %s" % response.text

        response_object = json.loads(response.text)

        self.temperature = response_object['location']['monitoring']['freeze']['temp']
        
        if self.debug:
            print "Current Temperature: %s" % self.temperature

    def get_location(self):
        
        if not self.uid:
            self.abort("You tried to get location without first having a User ID set.")
        
        location_data = {
            'no_persist': '0',
            'XDEBUG_SESSION_START': 'session_name',
        }
        
        URL = LOCATIONS_URL.replace('$UID$', self.uid)
        response = self.session.post(URL, data=location_data)
        response_object = json.loads(response.text)
        
        if self.debug:
            print "Location Response: %s" % response.text

        self.location = response_object['locations'].keys()[0]
        self.state = response_object['locations'][self.location]['system_state']

    def login(self, username, password):

        if not username or not password:
            sys.exit("You must provide a username and password.")

        login_data = {
            'name': username,
            'pass': password,
            'device_name': 'My iPhone',
            'device_uuid': str(uuid.uuid1()),
            'version': '1100',
            'no_persist': '1',
            'XDEBUG_SESSION_START': 'session_name',
        }

        response = self.session.post(LOGIN_URL, data=login_data)
        response_object = json.loads(response.text)
        
        if self.debug:
            print "Login Response: %s" % response.text
        
        self.username = response_object['username']
        self.session_id = response_object['session']
        self.uid = response_object['uid']

    def logout(self):
        
        logout_data = {
            'no_persist': '0',
            'XDEBUG_SESSION_START': 'session_name',
        }
        
        response = self.session.post(LOGOUT_URL)
        response_object = json.loads(response.text)
        
        if self.debug:
            print "Logout Response: %s" % response.text

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--username', help='Your Simplsafe Username', required=True)
    parser.add_argument('--password', help='Your Simplsafe Password', required=True)
    parser.add_argument('--state', help='Desired Alarm State', required=True)
    parser.add_argument('--debug', help='Output debugging information', required=False, default=False, action="store_true")

    args = vars(parser.parse_args())

    if args['state'] not in ('Off', 'Away', 'Home'):
        sys.exit("State must be Off, Away, or Home")

    s = SimpliSafe(args['debug'])

    s.login(args['username'], args['password'])
    s.get_location()
    s.set_state(args['state'].lower())
    
    print "System State: %s" % s.get_state()
    s.logout()
