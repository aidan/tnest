#!/usr/bin/env python3

import collections
import json
import unittest

from bs4 import BeautifulSoup

Property = collections.namedtuple('Property',
                                  ['name',
                                   'type',
                                   'bedrooms',
                                   'bathrooms',
                                   'amenities'])

class AirBnBScraper:

    @staticmethod
    def property_from_html(html):
        soup = BeautifulSoup(html, 'html.parser')

        # One of the json script tags has a nice json of the listing
        # in it
        json_scripts = soup.findAll(type='application/json') 
        datatext = None
        for snippit in json_scripts:
            if (snippit.attrs.get('data-hypernova-key', None) == 
                'p3show_marketplacebundlejs'):
                datatext = snippit
                break

        if not datatext:
            raise Exception("Could not find property json")

        # The json has leading/trailing HTML comment indicators which
        # need to be stripped before parsing
        data = json.loads(datatext.text[4:-3])
        # and down a few datetime.datetime.datetimes...
        listing = data['bootstrapData']["reduxData"]["marketplacePdp"]["listingInfo"]["listing"]

        # Get the property type from this weird thing
        for entry in listing["space_interface"]:
            if entry["label"] == 'Property type:':
                property_type = entry["value"]
                break
            
        # Build the list of amentities 
        amenities = []
        for amenity in listing["listing_amenities"]:
            if amenity["is_present"]:
                amenities.append(amenity["name"])

        # Everything else can be pulled directly
        property = Property(name=listing['name'],
                            type=property_type,
                            bedrooms=int(listing['bedrooms']),
                            bathrooms=int(listing['bathroom_label'].split(' ')[0]),
                            amenities=set(amenities))
        return property

class TestAirBnBScraper(unittest.TestCase):

    examples = [{'url': 'https://www.airbnb.co.uk/rooms/14531512?s=51',
                 'expected': Property(
                     name='Garden Rooms: Featured in Grand Designs Sept 2017',
                     type='Apartment',
                     bedrooms=0,
                     bathrooms=1,
                     amenities=set(['Family/Kid Friendly',
                                    'Wheelchair accessible',
                                    'Suitable for events',
                                    'Kitchen',
                                    'Wireless Internet',
                                    'Hair dryer',
                                    'TV',
                                    'Laptop friendly workspace',
                                    'Iron',
                                    'Essentials',
                                    'Shampoo',
                                    'Hangers',
                                    'Heating',
                                    'Private entrance',
                                    'High chair',
                                    'Pack ’n Play/travel crib',
                                    'First aid kit',
                                    'Smoke detector',
                                    'Cable TV',
                                    '24-hour check-in',
                                    'Carbon monoxide detector'
                     ]))
                },
                {'url': 'https://www.airbnb.co.uk/rooms/19278160?s=51',
                 'expected': Property(
                     name='York Place: Presidential Suite For Two',
                     type='Apartment',
                     bedrooms=1,
                     bathrooms=1,
                     amenities=set(['Kitchen',
                                    'Wireless Internet',
                                    'Hair dryer',
                                    'TV',
                                    'Laptop friendly workspace',
                                    'Iron',
                                    'Essentials',
                                    'Shampoo',
                                    'Washer',
                                    'Hangers',
                                    'Heating',
                                    'Private entrance',
                                    'Smoke detector',
                                    'Carbon monoxide detector'
                     ]))
                },
                {'url': 'https://www.airbnb.co.uk/rooms/19292873?s=51',
                 'expected': Property(
                     name='Turreted apartment near Edinburgh  Castle',
                     type='Apartment',
                     bedrooms=1,
                     bathrooms=1,
                     amenities=set(['Family/Kid Friendly',
                                    'Kitchen',
                                    'Wireless Internet',
                                    'Breakfast',
                                    'Hair dryer',
                                    'Laptop friendly workspace',
                                    'Essentials',
                                    'Shampoo',
                                    'Washer',
                                    'Hangers',
                                    'Heating',
                                    'Smoke detector',
                                    'First aid kit',
                                    'Safety card',
                                    'Fire extinguisher']))
                }
    ]

    def test_all(self):
        for ex in self.examples:
            file_name = ex['url'].split('/')[-1]
            with open('pages/'+file_name) as f:
                self._check_parser(f.read(None),
                                   ex['expected'])
                
    def _check_parser(self, string, expected):
        property = AirBnBScraper.property_from_html(string)
        self.assertEqual(expected.name, property.name)
        self.assertEqual(expected.type, property.type)
        self.assertEqual(expected.bedrooms, property.bedrooms)
        self.assertEqual(expected.bathrooms, property.bathrooms)
        self.assertEqual(expected.amenities, property.amenities)

if __name__ == '__main__':
    unittest.main()
    
