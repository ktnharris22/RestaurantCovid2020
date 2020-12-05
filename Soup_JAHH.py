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


#Function Searches for common typos iwithin the HTML data
#Returns the correct tag to remedy data output issues later on in the code

def preClean(stringList,tagList):
    cleanTag = ''
    for i in range(len(tagList)):
        if stringList.find(tagList[i]) != -1:
            cleanTag = tagList[i]
            return cleanTag    

#Function that clips desired data from string of data and returns string
#Calls clean function with removes line breaks and unnecessary spaces at start or ned of string.
def clip(stringData,startTag, endTag):
    clippedData = 'dataNotclipped'
    
    if startTag == endTag:
        sIndex = stringData.find(startTag)
        eIndex = stringData.find(endTag,sIndex+1)
        temp = stringData[sIndex + len(startTag):eIndex]
        clippedData = cleanUp(temp)
    
  
    else:    
        sIndex = stringData.find(startTag)
        eIndex = stringData.find(endTag)
        
        if startTag == 'PA':
            temp = stringData[sIndex + len(startTag):sIndex + len(startTag)+6]
            clippedData = cleanUp(temp)
        else:   
            temp = stringData[sIndex + len(startTag):eIndex]
            clippedData = cleanUp(temp)
    
    return clippedData

#Function that cleans data strings given a pre-set list of "fillers"
def cleanUp (stringData):
    newData = stringData.strip()
    fillerZ = ['\r\n', '<br/>', '</p>']
    for i in range(len(fillerZ)):
        cleanIndex = newData.find(fillerZ[i])
        if cleanIndex != -1: #checks to see if the specific filler is a part of the substring of data
            lenFiller = len(fillerZ[i])
            newData = newData[0:cleanIndex].strip() + ' ' + newData[cleanIndex+lenFiller:].strip()
            newData.strip()
    return newData #type string

#Function that takes in beautifulSouplList and parses data into a usable data struct for further processing
def parseData(beautifulSoupList):
    #Creating dataframe to return the parsed Beautiful soup data
    df=pd.DataFrame(columns = ['Name', 'Address', 'Zip','Boro', 'Post Date','Remove Date','Violation','Covid Situation'])
    #creating data parsing tags for searching string
    headerKeyWord = 'NOTE: ' #checks for non-restuarant data
    
    tagName_s = '<tr>\n<td style="cursor: default;">\n<p>'
    tagName_s2 = '<tr>\n<td style="cursor: default;">'

    tagName_e = '<br/>'
    
    tagAdd_s = '<br/>'
    tagAdd_e = '<br/>' #check to see if they are the same
    tagAdd_e2 = '<p>'
    
    tagZip_s = 'PA'
    tagZip_e = '</p>'
    tagZip_e2 = '<p>'

    #search for PA and then count 5 indices
    
    tagBoro_s = '<p>'
    tagBoro_e = '</p>'
    
    tagPDate_s = 'Posted: '
    tagPDate_s2 = 'Posted '
    tagpDate_e = '<br/>R'
    
    tagPRem_s = 'Removed:'
    tagPRem_e = '</p>\n<p>V'
    
    tagViol_s = 'Violation:<br/>' #violation tag
    tagViol_e = '</p>\n</td>\n</tr>'
        
    tagParamList = [['NAME',[tagName_s,tagName_s2] ,tagName_e],['ADDRESS',tagAdd_s,[tagAdd_e,tagAdd_e2]], ['ZIP',tagZip_s,tagZip_e], ['BORO',tagBoro_s, tagBoro_e],['POST',[tagPDate_s,tagPDate_s2],tagpDate_e],['Remove',tagPRem_s,tagPRem_e],['VIOLATION',tagViol_s,tagViol_e]]

    for i in range(len(beautifulSoupList)):
        rawParameter = str(beautifulSoupList[i])
        #checking to ensure that the rawparameter isn't heading information
        if rawParameter.find(headerKeyWord) == -1:
            lst=[]
            for j in range(len(tagParamList)): # tag here
                
                if type(tagParamList[j][1]) != str and type(tagParamList[j][2]) == str:
                    startT = preClean(rawParameter,tagParamList[j][1])
                    endT = tagParamList[j][2]
                elif type(tagParamList[j][2]) != str and type(tagParamList[j][1]) == str:   
                    startT = tagParamList[j][1]
                    endT = preClean(rawParameter,tagParamList[j][2])
                elif type(tagParamList[j][2]) != str and type(tagParamList[j][1]) != str:
                    startT = preClean(rawParameter,tagParamList[j][1])
                    endT = preClean(rawParameter,tagParamList[j][2])
                else: 
                    startT = tagParamList[j][1]
                    endT = tagParamList[j][2]
                
                temp = clip(rawParameter,startT,endT)
                
                
                print(tagParamList[j][0] + ': ' + temp)
                #print(startT)
                #print(endT)
                if len(temp)!=0:
                    #print(temp.rstrip())
                    lst.append(temp.rstrip())
            print(lst[0])
            print(len(lst))
            if len(lst)==7:
                if 'Covid' in lst[6] or 'COVID' in lst[6] or 'covid' in lst[6]:
                    df=df.append({'Name':lst[0], 'Address':lst[1], 'Zip':lst[2],'Boro':lst[3].strip('()'), 'Post Date':lst[4],'Remove Date':lst[5],'Violation':lst[6], 'Covid Situation':'COVID-19'},ignore_index=True)
                else:
                    df=df.append({'Name':lst[0], 'Address':lst[1], 'Zip':lst[2],'Boro':lst[3].strip('()'), 'Post Date':lst[4],'Remove Date':lst[5],'Violation':lst[6], 'Covid Situation':'No'},ignore_index=True)
    #print(df)
    return df
                    #print(type(temp))
                #Dhruva to create desired structure to input into larger data frame
                #tagParamList[j][0] 'Name' key
                #temp 'Name Data'
                
                
    
    #dataStruct = dict()
    
def main():
    
    #URL 
    
    countyURL = 'https://www.alleghenycounty.us/Health-Department/Programs/Food-Safety/Consumer-Alerts-and-Closures.aspx'
    
    page =\
        requests.get(countyURL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    header=['One','Two','Three','Four','Five','Six','Seven']
    data=pd.DataFrame()
    for item in header:
        accordionYearData= soup.find(id="collapse"+item)
        accordionYearData2= soup.find(id="headingOne")
        accordionYearList = accordionYearData.find_all('tr')#beautiful soup elements list
        data = data.append(parseData(accordionYearList),ignore_index=True)
    print(data)
    return data
#    #x2=accordionYearData2.find_all('</i>')


    #print(accordionYearData.prettify())
    #print(accordionYearData2.prettify())
    
#    restaurantData = accordionYearData.find("<tr>") #searches in HTML file for the detail information
    
    #calls program that prints out current weather condition information

if __name__ == '__main__': 
    a=main()
