# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import List
import spacy
import requests
import os

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount

class WeatherBot(ActivityHandler):

    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
        self.api_key = os.environ.get("OWM_API_KEY")

    def get_weather(self, city_name):
        api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(
            city_name, self.api_key)

        response = requests.get(api_url)
        response_dict = response.json()

        weather = response_dict["weather"][0]["description"]

        if response.status_code == 200:
            return weather
        else:
            print('[!] HTTP {0} calling [{1}]'.format(response.status_code,
                                                      api_url))
            return None

    async def on_members_added_activity(self, members_added: List[ChannelAccount],
                                        turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")

    async def on_message_activity(self, turn_context: TurnContext):
        statement = turn_context.activity.text
        rval = "Sorry I don't understand that. Please rephrase your statement."

        weather = self.nlp("Current weather in a city")
        statement = self.nlp(statement)
        min_similarity = 0.75

        if weather.similarity(statement) >= min_similarity:
            for ent in statement.ents:
                if ent.label_ == "GPE":  # GeoPolitical Entity
                    city = ent.text
                    break
                else:
                    rval = "You need to tell me a city to check."

            city_weather = self.get_weather(city)
            if city_weather is not None:
                rval = "In " + city + ", the current weather is: " + city_weather
            else:
                rval = "Something went wrong."

        return await turn_context.send_activity(MessageFactory.text(rval))
