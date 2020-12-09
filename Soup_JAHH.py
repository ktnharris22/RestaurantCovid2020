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
import re


# Function that pulls the Issue Type from the Alleghany County Website header

def pullHeader (soupHeaderData):
    #Types of Restaurant Notices
    header = 'Out_of_Scope'
    keyWords = ['Closure', 'Alert']
    headerStr = str(soupHeaderData)
    for i in range(len(keyWords)):
        if headerStr.find(keyWords[i]) != -1:
            header = keyWords[i].upper()
    return header

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
    temp = ''
    if startTag == endTag:
        sIndex = stringData.find(startTag)
        eIndex = stringData.find(endTag,sIndex+1)
        temp = stringData[sIndex + len(startTag):eIndex]
        clippedData = cleanUp(temp)
    
    else:    
        sIndex = stringData.find(startTag)
        eIndex = stringData.find(endTag)
        
        #Specific checker for zip code
        if startTag == 'PA':
            pattern = [' [0-9]{5}', '[0-9]{5}<br/>']   
            for i in range(len(pattern)):
                if len (re.findall(pattern[i],stringData)) != 0:
                    if pattern[i] == ' [0-9]{5}':
                        temp = re.findall(pattern[i],stringData)[0][0:6]
                    else: temp = re.findall(pattern[i],stringData)[0][0:5]
            clippedData = cleanUp(temp)
            if not clippedData:
                clippedData = 'NaN'
            
        else:   
            temp = stringData[sIndex + len(startTag):eIndex]
            clippedData = cleanUp(temp)
            if not clippedData:
                clippedData = 'NaN'
        
    
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
    tagAdd_e = '\r\n'
    tagAdd_e2 = '\r'
    tagAdd_e3 = '<p>'
    tagAdd_e4 = '<br/>' 
    
    tagZip_s = 'PA'
    tagZip_s2 = 'Pittsburgh'
    tagZip_e = '</p>'
    tagZip_e2 = '<p>'

    
    tagBoro_s = '<p>'
    tagBoro_e = '</p>'
    
    tagPDate_s = 'Posted: '
    tagPDate_s2 = 'Posted:'
    tagPDate_s3 = 'Posted '
    tagPDate_s4 = 'Posted'
    tagpDate_e = '<br/>R'
    
    tagPRem_s = 'Removed:'
    tagPRem_e = '</p>\n<p>V'
    
    tagViol_s = 'Violation:<br/>' #violation tag
    tagViol_e = '</p>\n</td>\n</tr>'
        
    tagParamList = [['NAME',[tagName_s,tagName_s2] ,tagName_e],['ADDRESS',tagAdd_s,[tagAdd_e,tagAdd_e2,tagAdd_e3,tagAdd_e4]], ['ZIP',tagZip_s,tagZip_e], ['BORO',tagBoro_s, tagBoro_e],['POST',[tagPDate_s,tagPDate_s2,tagPDate_s3,tagPDate_s4],tagpDate_e],['Remove',tagPRem_s,tagPRem_e],['VIOLATION',tagViol_s,tagViol_e]]
    temp = ''
    for i in range(len(beautifulSoupList)):
        rawParameter = str(beautifulSoupList[i])
        #checking to ensure that the rawparameter isn't heading information
        print('\n')
        if rawParameter.find(headerKeyWord) == -1:
            lst=[]
            for j in range(len(tagParamList)): # tag here
            
            #Specific address check and generalied checks
            #for returning parsed soup data
                if tagParamList[j][0] == 'ADDRESS':        
                    pattern = r'<br/>[ ]*[0-9]+[ ]*[0-9,A-Z]+.*'
                    rawAddList =  re.findall(pattern,rawParameter)
                    if len(rawAddList) == 0:
                        temp = 'NaN'
                    else:
                        addressPatterns = [r'<br/>.*<p>',r'<br/>.*<br/>',r'<br/>.*\r']
                        for k in range(len(addressPatterns)):
                            subString = re.findall(addressPatterns[k],rawAddList[0])
                            if len(subString) != 0:
                                startT = tagParamList[j][1]
                                endT = preClean(subString[0],tagParamList[j][2])
                                break
                        temp = clip(subString[0],startT,endT)
                elif type(tagParamList[j][1]) != str and type(tagParamList[j][2]) == str:
                    startT = preClean(rawParameter,tagParamList[j][1])
                    endT = tagParamList[j][2]
                    temp = clip(rawParameter,startT,endT)
                elif type(tagParamList[j][2]) != str and type(tagParamList[j][1]) == str:   
                    startT = tagParamList[j][1]
                    endT = preClean(rawParameter,tagParamList[j][2])
                    temp = clip(rawParameter,startT,endT)
                elif type(tagParamList[j][2]) != str and type(tagParamList[j][1]) != str:
                    startT = preClean(rawParameter,tagParamList[j][1])
                    endT = preClean(rawParameter,tagParamList[j][2])
                    temp = clip(rawParameter,startT,endT)
                else:  
                    startT = tagParamList[j][1]
                    endT = tagParamList[j][2]
                    temp = clip(rawParameter,startT,endT)
                
                
                #print(tagParamList[j][0] + ': ' + temp)
                if len(temp)!=0:
                    #print(temp.rstrip())
                    lst.append(temp.rstrip())
            #print(lst[0])
            #print(len(lst))
            if len(lst)==7:
                if 'Covid' in lst[6] or 'COVID' in lst[6] or 'covid' in lst[6]:
                    df=df.append({'Name':lst[0], 'Address':lst[1], 'Zip':lst[2],'Boro':lst[3].strip('()'), 'Post Date':lst[4],'Remove Date':lst[5],'Violation':lst[6], 'Covid Situation':'COVID-19'},ignore_index=True)
                else:
                    df=df.append({'Name':lst[0], 'Address':lst[1], 'Zip':lst[2],'Boro':lst[3].strip('()'), 'Post Date':lst[4],'Remove Date':lst[5],'Violation':lst[6], 'Covid Situation':'No'},ignore_index=True)
    return df

def cleanDate(df):
    #p='[A-Z][a-z]+.\s[0-9]+,\s[0-9]+'
    p='[A-Z][a-z]+.\s[0-9]+,.[0-9]+'
    for i in range(len(df)):
        print(i)
        if df.loc[i]=='PERMANENTLY CLOSED' or df.loc[i]=='NaN' or df.loc[i]=='' :
            continue
        else:
            df.loc[i]=re.findall(p,df.loc[i])[0]
    return df

def addPitt(df):
    for i in range(len(df)):
        if 'Pittsburgh, PA' in df['Address'].loc[i] or df['Address'].loc[i]=='NaN':
            continue
        else:
            df['Address'].loc[i]=df['Address'].loc[i]+' Pittsburgh, PA'
    return df
    

def getSoupDF():
    
    #Data URL 
    countyURL = 'https://www.alleghenycounty.us/Health-Department/Programs/Food-Safety/Consumer-Alerts-and-Closures.aspx'
    
    #Request page information & create soup variable
    page =\
        requests.get(countyURL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    #Keywords List to access Alleghany County Alert and Closure data (2018-2020)
    #header=['One','Two','Three','Four','Five','Six']
    header=['One','Two','Three','Five','Six']
    #header=['Two']
    #instantiate primary dataframe to be passed to API data
    data=pd.DataFrame()
    
    #Pull and concatenate accordion data for each set of data on site
    for item in header:
        accordionData = soup.find(id="collapse" + item)
        accordionYearDataHeader = soup.find(id="heading" + item)
        #print(accordionYearDataHeader)
        accordionYearList = accordionData.find_all('tr')#beautiful soup elements list
        plc_desc = pullHeader(accordionYearDataHeader)
        #print(header)
        #Append data frame to dtaframes of dataframes representing ...
        df=parseData(accordionYearList)
        df['Placard_desc']=pd.Series([plc_desc]*len(df))
        data = data.append(df,ignore_index=True)
        data=addPitt(data)
    #data['Post Date']=cleanDate(data['Post Date'])
    #data['Remove Date']=cleanDate(data['Remove Date'])
    #print(data)
    return data

    
def main():
    
    a=getSoupDF()
    return a

if __name__ == '__main__': 
   f=main()

