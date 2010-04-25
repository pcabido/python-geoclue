#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 - Paulo Cabido <paulo.cabido@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import sys ; sys.path.insert(0, '..')

import Geoclue as geoclue

def location_change():
    print "Location info changed:"
    print geolocation.get_location_info()
    print "\n"

geolocation = geoclue.DiscoverLocation()

#geolocation.connect(location_change)

geolocation.init()

location = geolocation.get_location_info()
print "Location: "
print location
print "\n"

#providers = geolocation.get_available_providers()
##print providers
#
## when a GPS is available, this will pass to the GPS provider
## this will change the master's default provider acording to the requirements
##geolocation.set_requirements(6, 0, True, (1 << 2))
#
## this will get the current position via GPS but it will continue to use
## the default master provider 
#geolocation.set_position_provider("Gpsd")
## as you can see, the signal function displays the GPS position :-)
#
#address = {}
#address['street'] = "Rua portuguesa num da porta"
#address['area'] = "Centro Historico"
#address['locality'] = "Evora"
#address['region'] = "Evora"
#address['country'] = "Portugal"
#address['countrycode'] = "PT"
## Localnet provider also uses the address 
#geolocation.set_address_provider("Manual", address)
#
#current_address_provider = geolocation.get_address_provider()
#print "Current address provider: %s" % current_address_provider
#
#current_position_provider = geolocation.get_position_provider()
#print "Current position provider: %s" % current_position_provider
#
#print "Reverse address for coordinates lat: 38.5833333 and lon: -7.8333333"
#revgeocoder = geolocation.reverse_position(38.5833333, -7.833333, 3)
#print revgeocoder
#print "\n"
#
## Compare the current position to a given position with a proximity factor of 500m
## It will return true or false
##print "Compare a position to the current position:"
##print "Position to compare, lat: %s lon: %s"
##geolocation.compare_position(LAT, LON, 0.5)
