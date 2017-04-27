### Author:         Ahmad Al-Dajani

### Description:    This Program is intended to retrieve the course schedule for Georgetown University Law Center's ("GULC") Curriculum Guide,
###                 and turn it into a manageable excel file that can be easily sorted according to credit, exam date, instructor, course type, time etc...

### Help:           Professor Paul Ohm's Computer Programming for Lawyers Course, taught at GULC. I had ZERO programming experience prior to this class,
###                 and it enabled me to develop sufficient proficiency in python programming to create this program and make my life easier

### Dependencies:   requests, beautifulSoup 4, urllib, re, csv
### Time:           2-3 Hours - to create a program that sorted through many courses, and made the course selection process simple and convenient. 
### DISCLAIMER:     Beware of sorting the spreadsheet by exam date as there are too many outliers for a consistent result. For the most part, dates and designations are accurate as they pretain to courses

import requests
import bs4
import urllib.parse
import re
import csv 

    # This is the URL for the GULC Curriculum Guide along with parameters
url = 'http://apps.law.georgetown.edu/curriculum/tab_schedules.cfm'
parameters = {'Status':'Schedule',
              'Type':'Letter',
              'Program': 'JD',   # This controls the program, you can switch the to 'LLM' instead of 'JD' to get schedules for LLM Programs
              'Year':39,
              'Term':'2017C',   # This Controls the Semester - Summer Semesters are usually in this format'YYYYB'; Fall is YYYYC; Spring is YYYYA
              'Letter':'ALL',    # This sorts the course by letter, I chose to view all courses available
              'Writing': 1     # to change from writing course schedule to exam course schedule simply comment this line out. DONT FORGET TO REMOVE THE PRECEDING COMMA IF YOU COMMENT THIS LINE OUT. 
                }
    # Create a CSV file named Course Guide (Term) and save it in the working directory

if parameters['Term'] == '2018A':
    if 'Writing' in parameters.keys():
        filename = 'CourseGuideGULCSpring2018WR.csv'
    else:
        filename = 'CourseGuideGULCSpring2018EX.csv'
elif parameters['Term'] == '2017C':
    if 'Writing' in parameters.keys():
        filename = 'CourseGuideGULCFall2017WR.csv'
    else:
        filename = 'CourseGuideGULCFall2017EX.csv'

fp = open(filename, 'w', newline='', encoding = 'latin-1')
    # Read the CSV file
reader = csv.reader(fp)

    # These are the headings that I would like to input into the first row of the newly created CSV
fieldNames = ['Course No.', 'CRN', 'Course Title', 'CR.', 'Faculty', 'Days', 'From-To', 'Exam/Paper']

    # Write the headings into the file
headingWriter = csv.DictWriter(fp, fieldNames)
headingWriter.writeheader()



    # Go to the URL with the above parameters and get the HTML from that URL, then store it as response variable
response = requests.get(url, params=parameters)
    # Have Beautiful Soup work its magic on the URL
soup = bs4.BeautifulSoup(response.text, 'html.parser')
    # If you inspect the curriculum guide page, this is where you will find the schedule table <table #schedMain
    # Select table rows from that table
rows = soup.select('tr')
for row in rows:
    try:
    # I had to skip an exception because the first tr is for table headers, as such it does not contain 'td' but 'th'
        cols = row.findAll("td")
          # trial and error allows you to figure out what the index for each column in the table is
        courseNo = cols[0].get_text()
            # the string retrieved from the first column contains some unnecssary text, so I narrowed it down using a Regex
        matchJDnum = re.match(r'\w+\-\d+\-\d+', courseNo)
        JDNum = matchJDnum.group(0)
            # Course Registration Numbers are in a seperate division within a division
        crn = cols[0].find('div').string
        crnMatch = re.search(r'\(.+?\)', crn)
        RegNo = crnMatch.group(0)
            # Course headings are available as a string in an aTag
        courseTitle = cols[1].find('a').string       
            # Course Credits
        credit = cols[2].get_text()       
            # Course Instructors
        instructors = cols[3].get_text()
        teachers = re.match(r'.*', instructors, flags=re.MULTILINE|re.DOTALL)
        professors = teachers.group(0)
            # Days for course
        day = cols[5].get_text()
            # Time for each course are within a seperate tag called <nobr>
        time = cols[6].find('nobr').string
            # Time String retrieved was too long to stick into a CSV field, so narrow it down to the minimum requirement
        timeMatch = re.match(r'\d+\:\d+\-\d+\:\d+', time, re.MULTILINE)
        courseTime = timeMatch.group(0)
            # Get the course classification or exam date
        classification = cols[7].text
        removeSpaces = re.sub(r"(\s+)", "", classification, flags=re.MULTILINE)
            # Gather all the information we retrieved, and stick it into a list, then write it to the csv file we created earlier.
        dataList = [JDNum, RegNo, courseTitle, credit, professors, day, courseTime, removeSpaces]
        writer = csv.writer(fp)
        writer.writerow(dataList)
    except Exception:
        pass
fp.close()

