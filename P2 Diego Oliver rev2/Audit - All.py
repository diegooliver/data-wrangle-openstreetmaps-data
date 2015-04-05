#!/usr/local/bin/python
# coding: latin-1

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

# Function to print the dictionary
def print_dict(d):
    keys = d.keys() # Returns a list of all keys in the dictionary
    for k in keys: # Checking each key
        v = d[k] # Assigns the value to v
        print "%s: %d" % (k, v) # Prints

# Function to print sorted
def print_sorted(d):
    keys = d.keys()
    keys = sorted(d)
    for k in keys:
        if d[k] > 100:
            v = d[k]
            print "%s: %d" % (k, v) 

# Function to accumulate the counts
def count_field(count, key): 
    count[key] += 1 # Accumulates the count

# Function to count elements tag based on the osm file
def elements(osm_file):    
    count = defaultdict(int)
    for event, elem in ET.iterparse(osm_file, events=('start', 'end')):        
        count_field(count, elem.tag) #Calls function to accumulate each element
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()
    print_dict(count)

# Function to count elements attributes based on the osm file
def element_parameters(osm_file, element):    
    lista = set() # Starts a test
    for event, elem in ET.iterparse(osm_file, events=('start', 'end')): # Function to IterParse              
        if elem.tag == element: # Proceeds if on the required element
            for key in elem.attrib.keys(): # Flows through each key in element
                if key not in lista:                
                    lista.add(key)
                    print key
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()

# Function to count elements within the TAG based on the osm file
def tagelements(osm_file):
    count = defaultdict(int)
    for event, elem in ET.iterparse(osm_file, events=('start', 'end')):              
        if elem.tag == "tag":   
            count_field(count, elem.attrib['k'])
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()
    print_sorted(count)

# Function to count values of the elements within TAG based on the osm file and TAG
def tagelementsvalues(osm_file, field):
    count = defaultdict(int)
    for event, elem in ET.iterparse(osm_file, events=('start', 'end')):              
        if elem.tag == "tag" and elem.attrib['k'] == field:   
            count_field(count, elem.attrib['v'])
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()
    print_dict(count)    

# Function to count other elements based on the osm file and field
def elementsvalues(osm_file, element, field):
    count = defaultdict(int)
    for event, elem in ET.iterparse(osm_file, events=('start', 'end')):              
        if elem.tag == element:
            for key in elem.attrib.keys():
                if key == field:
                    count_field(count, elem.attrib[key])
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()
    print_dict(count)

# Function to check if the keys have bad characters
def check_keys(osm_file):
    lower = re.compile(r'^([a-z]|_)*$')
    lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}    
    for event, elem in ET.iterparse(osm_file, events=('start', 'end')):    
        if elem.tag == "tag":
            if re.search(lower_colon, elem.get('k')) is not None:
                keys["lower_colon"] += 1
            elif re.search(lower, elem.get('k')) is not None:
                keys["lower"] += 1
            elif re.search(problemchars, elem.get('k')) is not None:
                keys["problemchars"] += 1
                print elem.get('k')
            else:
                keys["other"] += 1
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()        
    print keys

# Function to count unique users
def unique_users(osm_file):
    users = set()
    for event, elem in ET.iterparse(osm_file):
        if elem.get('uid') is not None:
            users.add(elem.get('uid'))
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()
    print users

# Defining street type regular expression and variable type
street_type_re = re.compile(r'^\w+\.?')#, re.IGNORECASE)
street_types = defaultdict(int)

# Function to check street names against expected types
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1

# Function to print the dictionary sorted
def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 

# Function to call the audit street when the inspected element relates to street
def street_check(osm_file):
    for event, elem in ET.iterparse(osm_file):
        if (elem.tag == "tag") and (elem.attrib['k'] == "addr:street"):
            audit_street_type(street_types, elem.attrib['v'])
        if event == 'end': #Clear iterparse so it won't end up iteratively building the entire tree
            elem.clear()               
    print_sorted_dict(street_types) 