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

import random

class Signal:
    class Slot:
        def __init__(self, func):
            self.__func = func

        def __call__(self, accum, *args, **kwargs):
            result = self.__func(*args, **kwargs)
            return accum(result)
            
    class Accumulator:
        def __call__(self, *args, **kwargs):
            return True
            
        def finalize(self):
            return None

    def __init__(self):
        self.__slots = []
        
    def create_accumulator(self):
        return self.Accumulator()

    # execute the slots
    def __call__(self, *args, **kwargs):
        accum = self.create_accumulator()
        for conn in xrange(len(self.__slots)):
            if not self.__slots[conn][1](accum, *args, **kwargs):
                break
        return accum.finalize()
    
    def find(self, conn):
        for i in xrange(len(self.__slots)):
            if self.__slots[i][0] == conn:
                return i
                
        return -1
    
    # create the connection name
    def new_connection(self):
        value = 0
        while self.find(value) >= 0:
            value = random.randint(1, 100000000)
        return value
    
    def connect(self, func):
        conn = self.new_connection()
        self.__slots.append([conn, Signal.Slot(func)])
        return conn
        
    # disconnect a slot
    def disconnect(self, conn):
        result = self.Find(conn)
        if result >= 0:
            del self.__slots[result]
            
    # disconnect all slots
    def disconnect_all(self):
        self.__slots = []
        
    