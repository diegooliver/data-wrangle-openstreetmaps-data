#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
phonechars = re.compile(r'[=\(\)\-\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

# Function to clean the phone numbers
def clean_phone(entry): # Receives the phone number entry
    better_phone = entry # Initializes better_phone
    better_phone = re.sub(phonechars, '', entry) # Removes unwanted characters
    #The next lines check various cases of bad numbers and correct them. It bases the correction on its length.
    if len(better_phone) == 13:
        better_phone = '+55 (41) ' + better_phone[5:9] + '-' + better_phone[9:13]
    elif len(better_phone) == 12:
        better_phone = '+55 (41) ' + better_phone[4:8] + '-' + better_phone[8:12]
    elif len(better_phone) == 11:
        better_phone = '+55 (41) ' + better_phone[3:7] + '-' + better_phone[7:11]           
    elif len(better_phone) == 10:
        better_phone = '+55 (41) ' + better_phone[2:6] + '-' + better_phone[6:10]
    elif len(better_phone) == 9:
        better_phone = ''
    elif len(better_phone) == 8:
        better_phone = '+55 (41) ' + better_phone[0:4] + '-' + better_phone[4:8]
    return better_phone # Returns the adjusted phone to the main function

# Function to clean the post codes
def clean_postcode(entry): # Receives the postcode entry
    better_postcode = entry # Initializes better_postcode
    #The next lines check various cases of bad post codes and correct them.
    #It bases the correction on the base format a postal code should have.
    if entry[0] == ' ':
        better_postcode = entry[1:3] + entry[4:7] + "-" + entry[8:11] # Checks if the first digit is blank        
    elif len(entry) > 8 and "-" == entry[6] and "." == entry[2]:
        better_postcode = entry[0:2] + entry[3:6] + "-" + entry[7:10] #Checks the length and other characters than numbers
    elif len(entry) > 7 and "-" != entry[5]:
        better_postcode = entry[0:5] + "-" + entry[5:9] #Check if the postcode already follows the golden standard
    elif len(entry) < 9:
        better_postcode = '00000-000' #If not enough data, changes to all 0s value
    return better_postcode # Returns the adjusted postcode to the main function

# Function to clean the websites
def clean_site(entry):
    better_site = entry # Initializes better_site
    #The next if block checks if the website starts with the standard format. If not, adds to it.
    if entry[0:7] != "http://" and entry[0:8] != "https://": 
        better_site = "http://" + entry # Adjusts the entry
    return better_site # Returns the adjusted site to the main function

# Function to clean street names
def clean_street(entry):
    mapping = { "AVENIDA": "Avenida", # Defines the mapping between wrong entries and its correction
            "Av ": "Avenida ",
            "Avda.": "Avenida",
            "Av. ": "Avenida " ,
            "Aveninda": "Avenida",
            "Al. ": "Alameda ",
            "Br ": "BR ",
            "R. ": "Rua ",
            " Rua": "Rua",
            "Rod. ": "Rodovia "}
    better_street = entry # Initializes better_street
    for item in mapping.keys(): # Initiates the routine to use each key of the mapping
        match = re.search(item, entry) #Searches for the keys on the entry
        if match:
            better_street = re.sub(item, mapping[item], entry) #Replaces the found key by its mapping
    return better_street #Returns the better street to the main function

# This function shapes the elements so they can be added to the database
def shape_element(element):
    node = {} # Initializes node
    node['created'] = {} #Initializes the key created within node
    node['type'] = [] #Initializes type within node
    if element.tag == "node" or element.tag == "way": #Checks if the tag is node or way
        for k, v in element.attrib.iteritems(): #Iterates through the tag attributes            
            if element.tag: #Assigns type as the element.tag (node or way)
                node['type'] = element.tag 
            if k in CREATED: #If K is present on CREATED list, adds the key to the node: created: {key: value}
                node['created'][k] = v 
            elif k in ['lat','lon']: #Check if K is lat and lon
                if 'pos' not in node:
                    node['pos'] = [] #Initializes key pos if not already in
                node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])] #Assigns the lat and lon as float values to the pos key
            else:
                node[k] = v # Create the other keys within node, assigning its v value
        for tag in element.findall('tag'): # For statement to go through all 'tag' tags
            if re.search(problemchars, tag.attrib['k']) is None: #Confirms that its K value has no problematic characters before moving on
                if tag.attrib['k'] == 'addr:street' and tag.attrib['k'] != 'addr:street:name' and tag.attrib['k'] != 'addr:street:prefix' and tag.attrib['k'] != 'addr:street:type':
                #Uses only the tags that have as K addr:street, ignoring the ones that have additional name, prefix and type attributes
                    if 'address' not in node:
                        node['address'] = {} #Initializes key address if not yet created             
                    node['address']['street'] = clean_street(tag.attrib['v']) #Assigns the cleaned value to address, street
                elif tag.attrib['k'] == 'addr:housenumber': #Checks if the K is the house number
                    if 'address' not in node:
                        node['address'] = {} #Adds the address as key if not yet there
                    node['address']['housenumber'] = tag.attrib['v'] #Assigns the value to the address, housenumber key
                elif tag.attrib['k'] == 'phone':
                    node['phone'] = clean_phone(tag.attrib['v']) #Assings the cleaned phone to phone key
                elif tag.attrib['k'] == 'addr:postcode': #Checks if K is the postcode
                    if 'address' not in node:
                        node['address'] = {} #Initializes key address if not yet created
                    node['address']['postcode'] = clean_postcode(tag.attrib['v']) #Assigns cleaned post codes to the node address, postcode key                
                elif tag.attrib['k'] == 'website':
                    node['website'] = clean_site(tag.attrib['v']) #Assigns  cleaned website to the node website key
                else:
                    node[(tag.attrib['k'])] = tag.attrib['v'] #Creates the remaining entries through the key and values pairs

        if element.tag == "way": #Proceeds if element is a way
            node['node_refs'] = [] #Initiaalizes the key node_refs
            for tag in element.iter("nd"):
                node['node_refs'].append(tag.attrib['ref']) #Appends the ref to the node_refs
        return node #Returns the built node
    else:
        return None #Returns None if other than node or way

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element) #Shapes the element calling shape_element function
            if el:
                data.append(el) #Appends the shaped element to data
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    data = process_map('curitiba.osm', False) #Processes the chosen map
    #pprint.pprint(data)
if __name__ == "__main__":
    test()