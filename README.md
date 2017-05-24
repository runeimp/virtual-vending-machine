Virtual Vending Machine
=======================


Python
------

### Vending Machine App

Python3 and Kivy

#### Contents

* Baby Elephants
* Clown Noses
* Cotton Candy
* Juggling Clubs
* Popcorn
* Show Tickets


### Testing App

Make a little tool to communicate with and test your vending machine.  Command-line, web, whatever you like.

Python3 and Kivy


Redis
-----

Database and communications hub.

### Events

| Node            | Method    | Event                | Notes            |
| ----            | ------    | -----                | -----            |
| vending machine | SUBSCRIBE | user inserts coin    |                  |
| vending machine | SUBSCRIBE | user selects product |                  |
| vending machine | PUBLISH   | dispense message     | If money >= cost |
| vending machine | PUBLISH   | dispense change      | If money > cost  |


### Redis Keys

* product id
* amount of money inserted (so we can display this info on the vending machine screen)


Testing
-------

I've setup a Makefile to run tasks. Simply run `make` to get a list of options.


"Features"
---------

The channel handler thread for `vendingremote.py` doesn't close like it's supposed to when the app is closed. Probably need fresh eyes to find the issue.

