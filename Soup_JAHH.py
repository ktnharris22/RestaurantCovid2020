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

#Function that clips desired data from string of data and returns string
#Calls clean function with removes line breaks and unnecessary spaces at start or ned of string.
def clip(stringData,startTag, endTag):
    sIndex = stringData.find(startTag)
    eIndex = stringData.find(endTag)
    temp = stringData[sIndex + len(startTag):eIndex]
    clippedData = cleanUp(temp)
    return clippedData

#Function that cleans data strings given a pre-set list of "fillers"
def cleanUp (stringData):
    newData = stringData
    fillerZ = ['\r\n']
    for i in range(len(fillerZ)):
        cleanIndex = newData.find(fillerZ[i])
        if cleanIndex != -1: #checks to see if the specific filler is a part of the substring of data
            lenFiller = len(fillerZ[i])
            newData = newData[0:cleanIndex+lenFiller].strip() + ' ' + newData[cleanIndex+lenFiller:].strip()
    return newData #type string

#Function that takes in beautifulSouplList and parses data into a usable data struct for further processing
def parseData(beautifulSoupList):
    
    #creating data parsing tags for searching string
    headerKeyWord = 'NOTE: ' #checks for non-restuarant data
    
    tagName_s = '<tr>\n<td style="cursor: default;">'
    tagName_e = '<br/>'
    
    tagAdd_s = '<br/>'
    tagAdd_e = '<br/>' #check to see if they are the same
    
    tagZip_s = 'PA'
    tagZip_e = '<p>'
    
    tagBoro_s = '<p>'
    tagBoro_e = '</p>'
    
    tagPDate_s = 'Posted: '
    tagpDate_e = '<br/>'
    
    tagPRem_s = 'Removed:'
    tagPRem_e = '</p>'
    
    tagViol_s = 'Violation:<br/>' #violation tag
    tagViol_e = '</p>\n</td>\n</tr>'
        
    tagParamList = [['NAME',tagName_s,tagName_e],['ADDRESS',tagAdd_s,tagAdd_e], ['ZIP',tagZip_s,tagZip_e], ['BORO',tagBoro_s, tagBoro_e],['POST',tagPDate_s,tagpDate_e],['Remove',tagPRem_s,tagPRem_e],['VIOLATION',tagViol_s,tagViol_e]]

    for i in range(len(beautifulSoupList)):
        rawParameter = str(beautifulSoupList[i])
        #checking to ensure that the rawparameter isn't heading information
        if rawParameter.find(headerKeyWord) == -1:
            for j in range(len(tagParamList)):
                startT = tagParamList[j][1]
                endT = tagParamList[j][2]
                temp = clip(rawParameter,startT,endT)
                
                #Dhruva to create desired structure to input into larger data frame
                #tagParamList[j][0] 'Name' key
                #temp 'Name Data'
                
                
    
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
    a=3
    #calls program that prints out current weather condition information

if __name__ == '__main__': 
    main()
