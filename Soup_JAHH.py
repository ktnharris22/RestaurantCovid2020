#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 17:23:51 2020

@author: jaihhunter-hill
"""

#https://docs.google.com/document/d/1epSaWCh70pPPcMuK7Tz2fRdXuuODRg1mLiHChS-S4XQ/edit

import requests
import sys
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


#def createDF(): df=pd.DataFrame(columns = ['Name', 'Address', 'Posted on','Removed on','Violation'])return df


#Function that cleans data strings given a pre-set list of "fillers" 
def cleanUp (stringData):
    newData = ''
    
    fillerZ = ['\r\n']
    
    for i in range(len(fillerZ)):
        lenFiller = len(fillerZ[i])
        cleanIndex = stringData.find(fillerZ[i])
        newData = stringData[0:cleanIndex+lenFiller].strip() + ' ' + stringData[cleanIndex+lenFiller:].strip()
    return newData #type string

#Function that takes in beautifulSouplList and parses data into a usable data struct for further processing
def parseData(beautifulSoupList):
    
    #creating data parsing tags for searching string
    headerKeyWord = 'NOTE: ' #checks for non-restuarant data
    tagRestName = '<tr>\n<td style="cursor: default;">'
    
    tagViol = 'Violation:<br/>' #violation tag
    lenTagViol = len(tagViol)
    
    tagPost = 'Posted: '
    lenTagPost = len(tagPost)

    tagRemove = 'Removed: '
    lenTagRemove = len(tagRemove)
    
    tagEnd = '</p>\n</td>\n</tr>'
    lenTagEnd = len(tagEnd)
    
    
    for i in range(len(beautifulSoupList)):
        rawParameter = str(beautifulSoupList[i])
        if rawParameter.find(headerKeyWord) == -1:
            
            violIndex = rawParameter.find(tagViol)
            endIndex = rawParameter.find(tagEnd)
            temp = rawParameter[violIndex+lenTagViol:endIndex]
            rawParameter = cleanUp(rawParameter)
    
    
    dataStruct = dict()
    


def main():
    
    #URL 
    
    countyURL = 'https://www.alleghenycounty.us/Health-Department/Programs/Food-Safety/Consumer-Alerts-and-Closures.aspx'
    
    page =\
        requests.get(countyURL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    
    accordionYearData= soup.find(id="collapseOne")
    accordionYearData2= soup.find(id="headingOne")
    
    accordionYearList = accordionYearData.find_all('tr')#beautiful soup elements list
    
    data = parseData(accordionYearList)
    
    #x2=accordionYearData2.find_all('</i>')


    print(accordionYearData.prettify())
    print(accordionYearData2.prettify())
    
    restaurantData = accordionYearData.find("<tr>") #searches in HTML file for the detail information
    
    #calls program that prints out current weather condition information

if __name__ == '__main__': 
    main()
