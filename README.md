simplisafe-python
=================

A hacky-hack Python wrapper to set the state of your SimpliSafe alarm system.

It's not the most elegant solution, as it logs in and out every time, but this way you don't have to worry that your login cookie has expired. They don't have a real API, this is just what their mobile app does if you sniff the network traffic.

###Usage:###


    $ python simplisafe.py --username YOUR_USERNAME --password YOUR_PASSWORD --state DESIRED_ALARM_STATE --debug

Alarm state can be *Off*, *Home*, or *Away*. (case-sensitive)
