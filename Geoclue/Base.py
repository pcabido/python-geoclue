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

import os
import sys
import math

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject

import geoclue
from Signal import Signal

DBusGMainLoop(set_as_default=True)

class DiscoverLocation:
    """ Discovers the location form the best available provider

    L{DiscoverLocation} is a object that provides a nice API interface
    for Geoclue.
    """
    
    def __init__(self, providers_path="/usr/share/geoclue-providers"):
        """Construct a L{DiscoverLocation} object.
        
        @param providers_path: The path to the providers. The default
        path to the providers is /usr/share/geoclue-providers.
        """
        self.bus = dbus.SessionBus()
        
        self.signal = Signal()
        
        # stores the location info
        self.location_info = {}
        
        # Insipered by Pierre-Luc Beaudoin - geoclue_properties.py
        # TODO: add an exception to this part of the code in case of the wrong 
        # or nonexisting dir
        self.providers = []
        
        dir = os.listdir(providers_path)
        
        for filename in dir:
            (name, ext) = os.path.splitext(filename)

            if ext == ".provider":
                complete = os.path.join(providers_path, filename)
                provider = geoclue.GeoclueProvider (complete)
                self.providers.append([provider,
                  provider.name,
                  provider.interfaces & geoclue.INTERFACE_ADDRESS,
                  provider.interfaces & geoclue.INTERFACE_POSITION,
                  provider.interfaces & geoclue.INTERFACE_GEOCODE,
                  provider.interfaces & geoclue.INTERFACE_REVERSE_GEOCODE,
                  provider.service,
                  provider.path
                  ])
    
    def init(self, accuracy=geoclue.ACCURACY_LEVEL_COUNTRY, resource=geoclue.RESOURCE_NETWORK):
        """Initializes Geoclue.
        
        @param accuracy: The desired accuracy.
        @param resource: The resource to be used.
        """
        self.accuracy = accuracy
        self.resource = resource
        
        try:
            self.master = self.bus.get_object(geoclue.MASTER_IFACE, geoclue.MASTER_PATH)
            self.client = self.bus.get_object(geoclue.MASTER_IFACE, self.master.Create())
            
            # connects to detect changes on the address and position providers
            self.client.connect_to_signal("AddressProviderChanged", self.on_address_provider_changed)
            self.client.connect_to_signal("PositionProviderChanged", self.on_position_provider_changed)
            
            self.address = dbus.Interface(self.client, dbus_interface=geoclue.ADDRESS_IFACE)
            self.address.connect_to_signal("AddressChanged", self.on_address_changed)
            self.client.AddressStart()
            
            self.position = dbus.Interface(self.client, dbus_interface=geoclue.POSITION_IFACE)
            self.position.connect_to_signal("PositionChanged", self.on_position_changed)
            self.client.PositionStart()
            
            self.client.SetRequirements(self.accuracy, 0, True, self.resource)
        
            try:
                self.on_address_changed(*self.address.GetAddress())
            except Exception, e:
                return False
                
            try:
                self.on_position_changed(*self.position.GetPosition())
            except Exception, e:
                return False
            
            return True
        except Exception, e:
            print "Error: %s" % e
            return False
       
    def provider_status(self, provider):
        """Checks a provider's status.
        
        @param provider: A provider instance.
        @return: The status.
        """
        obj = dbus.Interface(provider.get_proxy(), dbus_interface=geoclue.GEOCLUE_IFACE)
        status = obj.GetStatus()
        
        if status == geoclue.STATUS_ERROR:
            return "error"
        elif status == geoclue.STATUS_UNAVAILABLE:
            return "unavailable"
        elif status == geoclue.STATUS_ACQUIRING:
            return "acquiring"
        elif status == geoclue.STATUS_AVAILABLE:
            return "available"
        else:
            return "error"
    
    def provider_info(self, provider):
        """Returns the provider's Info.
        
        @return: A dictionary with the provider's name and descripiton.
        """
        obj = dbus.Interface(provider.get_proxy(), dbus_interface=geoclue.GEOCLUE_IFACE)
        info = obj.GetProviderInfo()
        tmp = {}
        tmp['name'] = str(info[0])
        tmp['description'] = str(info[1])
        return tmp

    def set_requirements(self, accuracy, time, require_updates, resource):
        """Set the client requirements.
        
        @param accuracy: The required minimum accuracy.
        @param time: The minimum time between update signals.
        @param require_updates: C{True} if updates are required or C{False} if updates 
        are not required.
        @param resource: The resources that are allowed to be used.
        """
        self.accuracy = accuracy
        self.resource = resource
        self.client.SetRequirements(accuracy, time, require_updates, allowed_resources)
            
    # provider changed methods, not really being used but it's useful to have 
    # them here just in case
    def on_address_provider_changed(self, name, description, service, path):
        #print "Address provider changed"
        pass
    
    def on_position_provider_changed(self, name, description, service, path):
        #print "Position provider changed"
        pass
    
    def update_location_address(self, address):
        """Updates the the location's address with the given C{address}.
        
        @address: The new address.
        """
        if address.has_key('street'):
            self.location_info['street'] = address['street']

        # TODO: postalcode ?
        
        if address.has_key('area'):
            self.locatio_info['area'] = address['area']

        if address.has_key('locality'):
            self.location_info['locality'] = address['locality']

        if address.has_key('country'):
            self.location_info['country'] = address['country']

        if address.has_key('region'):
            self.location_info['region'] = address['region']
        
        if address.has_key('countrycode'):
            self.location_info['countrycode'] = address['countrycode']
    
    def on_address_changed(self, timestamp, address, accuracy):
        """When the address changes the location info dictionary is updated.
        
        @param timestamp: The timestamp.
        @param address: The new address.
        @accuracy: The accuracy.
        """
        self.location_info['address_timestamp'] = timestamp
        self.update_location_address(address)
        self.signal()
        
    def on_position_changed(self, fields, timestamp, latitude, longitude, altitude, accuracy):
        """When the position changes the location info dictionary is updated.
        
        @param fields: The fields.
        @param timestamp: The timestamp.
        @param latitude: The new latitude.
        @param longitude: The new longitude.
        @param altitude: The new altitude.
        @param accuracy: The accuracy.
        """
        #print accuracy # I used this print to check the accuracy format
        self.location_info['position_timestamp'] = timestamp
        self.location_info['latitude'] = latitude
        self.location_info['longitude'] = longitude
        self.location_info['altitude'] = altitude
        self.signal()

    # returns the current values for location and position
    def get_location_info(self):
        """Returns the location info dictionary.
        
        @return: The location info dictionary.
        """
        return self.location_info
    
    def get_available_providers(self):
        """Returns the available providers.
         
        @return: A list of dictionarys,
        [PROVIDER, ADDRESS, POSITION, GEOCODING, REVERSE GEOCODING],
        with the name and True of False for supporting each of them
        """ 
        current_providers = []
        for provider in self.providers:
            tmp = {}
            tmp['name'] = provider[1]
            if provider[2] != 0:
                tmp['address'] = True
            else:
                tmp['address'] = False
                
            if provider[3] != 0:
                tmp['position'] = True
            else:
                tmp['position'] = False
                
            if provider[4] != 0:
                tmp['geocoding'] = True
            else:
                tmp['geocoding'] = False
                
            if provider[5] != 0:
                tmp['revgeocoding'] = True
            else:
                tmp['revgeocoding'] = False
            
            tmp['object'] = provider[0]
            tmp['service'] = provider[6]
            tmp['path'] = provider[7]
                
            current_providers.append(tmp)    
        
        return current_providers
    
    def set_position_provider(self, provider_name):
        """Set the position provider to a given C{provider_name} (if exists).
        
        @param provider_name: The provider's name
        @return: C{True} if the provider exists or C{False} if a provider
        does not exist.
        """
        provider_exists = False
        for provider in self.providers:
            if provider[1].lower() == provider_name.lower() and provider[3] != 0:
                current_provider = provider
                provider_exists = True
                break
        
        if not provider_exists:
            return False
        
        try:
            tmp_provider = current_provider[0].get_proxy()
            self.position = dbus.Interface(tmp_provider, dbus_interface=geoclue.POSITION_IFACE)
        except Exception, e:
            print "D-Bus error: %s" % e
            return False
            
        try:
            self.on_position_changed(*self.position.GetPosition())
        except Exception, e:
            print e
            
        return True
    
    def validate_address(self, address):
        """Receives the address and validates/corrects it.
        
        @param address: The address dictionary.
        @return: The address (with possible corrections).
        """
        tmp_address = {}
        if address.has_key('street'):
            tmp_address['street'] = address['street']
        else:
            tmp_address['street'] = ""
        
        # TODO: postalcode ?
        
        if address.has_key('area'):
                tmp_address['area'] = address['area']
        else:
            tmp_address['area'] = ""
        
        if address.has_key('locality'):
                tmp_address['locality'] = address['locality']
        else:
            tmp_address['locality'] = ""
        
        if address.has_key('country'):
            tmp_address['country'] = address['country']
        else:
            tmp_address['country'] = ""
            
        if address.has_key('region'):
            tmp_address['region'] = address['region']
        else:
            tmp_address['region'] = ""
            
        if address.has_key('countrycode'):
            tmp_address['countrycode'] = address['countrycode']
        else:
            tmp_address['countrycode'] = ""
            
        return tmp_address
    
    # TODO: add "valid-for" to continue to use the given provider
    def set_address_provider(self, provider_name, address=None):
        """Set the address provider
        
        @param provider_name: the provider's name
        @param address: the new address (for Manual and Localnet providers)
        @returns:  C{True} if the provider exists or C{False} if a provider
        does not exist.
        """
        provider_exists = False
        for provider in self.providers:
            if provider[1].lower() == provider_name.lower() and provider[2] != 0:
                current_provider = provider
                provider_exists = True
                break
            
        if not provider_exists:
            return False
        
        try:
            if (provider_name.lower() == "manual" or provider_name.lower() == "localnet") and address != None:
                tmp_provider = current_provider[0].get_proxy()
                tmp_provider.SetAddress(0, self.validate_address(address))
                self.address = dbus.Interface(tmp_provider, dbus_interface=geoclue.ADDRESS_IFACE)
            elif (provider_name.lower() == "manual" or provider_name.lower() == "localnet") and address == None:
                return False
            else:
                self.address = dbus.Interface(current_provider[0].get_proxy(), dbus_interface=geoclue.ADDRESS_IFACE)
        except Exception, e:
            print "D-Bus error: %s" % e
            return False
            
        try:
            self.on_address_changed(*self.address.GetAddress())
        except Exception, e:
            print e
            
        return True
    
    def get_position_provider(self):
        """Returns the name of the current position provider.
        
        @return: The name of the current position provider.
        """
        return self.client.GetPositionProvider()[0]
    
    def get_address_provider(self):
        """Returns the name of the current address provider.
        
        @return: The name of the current address provider.
        """
        return self.client.GetAddressProvider()[0]
    
    def compare_position(self, latitude, longitude, proximity_factor=None):
        """Compare the current position to a given position.
        
        Note: ploum's contribution
        
        @param latitude: latitude of the position
        @param longitude: longitude of the position
        @param proximity_factor: the near by proximity factor. ie, 0.5 is 500 meters
        """
        if proximity_factor == None:
            # 500 meters
            dis_max = 0.5
        else:
            dis_max = proximity_factor
        
        # todo_later : (calibration must be done with a well known distance )
        #This method assumes a spheroidal model for the earth with 
        #an average radius of 6364.963 km. 
        #The formula is estimated to have an accuracy of about 200 metres 
        #over 50 km, but may deteriorate with longer distances.
        #source : http://www.ga.gov.au/geodesy/datums/distance.jsp
        dl = self.location_info['latitude'] - latitude
        dg = self.location_info['longitude'] - longitude
        term1 = 111.08956 * (dl + 0.000001)
        term2 = math.cos(self.location_info['latitude'] + (dl/2))
        term3 = (dg + 0.000001) / (dl + 0.000001)
        d = term1 / math.cos(math.atan(term2 * term3))
        result =  math.fabs(d) < dis_max 
        return result
    
    def reverse_position(self, latitude, longitude, accuracy):
        """Returns an address that corresponds to a given position.
        
        @param latitude: The position's latitude.  
        @param longitude: The position's longitude.
        @param accuracy: The accuracy.
        @return: An address.
        """
        provider_exists = False
        for provider in self.providers:
            if provider[1].lower() == "Geonames Provider".lower():
                current_provider = provider
                provider_exists = True
                break
            
        if not provider_exists:
            return None
        
        try:
            revgeocoder = dbus.Interface(current_provider[0].get_proxy(), geoclue.REVERSE_IFACE)
            revaddress = revgeocoder.PositionToAddress(float(latitude), float(longitude), (accuracy, 0, 0))
            
            #add the values to the address of the location variable
            tmp_address = {}
            for key, item in revaddress[0].items():
                tmp_address[unicode(key)] = unicode(item)
            
            return self.validate_address(tmp_address)
        except Exception, e:
            print "D-Bus error: %s" % e
            return None
    
    def connect(self, func):
        """Connects a given function to the signal.
        The signal action if any change to the info location dictionary.
        
        @param func: The function to connect to the signal.
        """
        self.signal.connect(func)
    
    def disconnect(self, func):
        """Disconnects a given function from the signal.
        
        @param func: The function to disconnect from the signal.
        """
        self.signal.disconnect(func)
    
