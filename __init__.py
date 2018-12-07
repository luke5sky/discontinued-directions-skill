# Copyright 2018 Lukas Gangel
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import traceback
import logging

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from mycroft.audio import wait_while_speaking 
from urllib.request import Request, urlopen
from mycroft.util.log import getLogger

logger = getLogger(__name__)


__author__ = 'luke5sky'

class directionsSkill(MycroftSkill):

    def __init__(self):
        super(directionsSkill, self).__init__(name="directionsSkill")
        
    @intent_handler(IntentBuilder("").require("Directions").require("Give").require("FromLocation").require("ToLocation").build())
    def handle_directions__intent(self, message):
        self.apikey = self.settings.get('apiKey', '')
        self.myunit = self.settings.get('Unit','')
        fromaddr = message.data.get("FromLocation", None).replace(" to", "")
        toaddr = message.data.get("ToLocation", None)

        try:
            headers = {'Accept': 'application/json; charset=utf-8'}
            origfrom = fromaddr
            origto = toaddr
            fromaddr = fromaddr.replace(" ","%20")
            toaddr = toaddr.replace(" ","%20")
            unit = (self.myunit.lower())
    
            # parse input to coordinations
            fromcoords = Request('https://api.openrouteservice.org/geocode/search?api_key='+self.apikey+'&text='+fromaddr+'&layers=address,region,country&size=1', headers=headers)
            from_body = urlopen(fromcoords).read()
            fromdata = json.loads(from_body.decode('utf-8'))
            fromcoord1 = str(fromdata['features'][0]['geometry']['coordinates'][0])
            fromcoord2 = str(fromdata['features'][0]['geometry']['coordinates'][1])
    
            tocoords = Request('https://api.openrouteservice.org/geocode/search?api_key='+self.apikey+'&text='+toaddr+'&layers=address,region,country&size=1', headers=headers)
            to_body = urlopen(tocoords).read()
            todata = json.loads(to_body.decode('utf-8'))
            tocoord1 = str(todata['features'][0]['geometry']['coordinates'][0])
            tocoord2 = str(todata['features'][0]['geometry']['coordinates'][1])
            
            fromcoord1 = fromcoord1.replace(" ", "")
            fromcoord2 = fromcoord2.replace(" ", "")
            tocoord1 = tocoord1.replace(" ", "")
            tocoord2 = tocoord2.replace(" ", "")
            # get directions
            
            request =('https://api.openrouteservice.org/directions?api_key='+self.apikey+'&coordinates='+fromcoord1+','+fromcoord2+'%7C'+tocoord1+','+tocoord2+'&profile=driving-car&format=json&units='+unit+'&language=en&geometry=false&instructions=false')#, headers=headers)
            response_body = urlopen(Request(request, headers=headers)).read()
            data = json.loads(response_body.decode('utf-8'))
            distance = (data['routes'][0]['summary']['distance'])
            if unit=="km":
               unit = "kilometers"
            elif unit=="mi":
               unit = "miles"
            time = (data['routes'][0]['summary']['duration'])
            if time < 60:
               time = int(time)
               time = str(time) + " seconds"
            elif time < 3600:
               time = time/60
               time = int(time)
               time = str(time) + " minutes"
            elif time < 86400:
               timehour = time/60/60
               timeminutes = ((int(timehour)*60*60)-time)*(-1)
               timeminutes = timeminutes/60
               timeminutes=int(timeminutes)
               timehour=int(timehour)
               time = str(timehour) + " hours "+ str(timeminutes) + " minutes"
            else:
               time = str(time) + " days"
            distance = round(distance, 2)
            dist = str(distance)+ " " + unit
            hours = str(time)
            
            self.speak_dialog('result', {'FROM': origfrom, 'TO': origto, 'HOURS': hours, 'DISTANCE': dist}) 
        except Exception as e:
            logging.error(traceback.format_exc())
            self.speak_dialog('sorry')
        logger.info("Request finished")

    def shutdown(self):
        super(directionsSkill, self).shutdown()

    def stop(self):
        pass

def create_skill():
    return directionsSkill()
