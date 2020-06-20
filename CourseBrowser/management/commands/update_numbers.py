from datetime import datetime
from django.core.management import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from CourseBrowser.models import Courses
from decimal import Decimal
import ssl
import requests
from bs4 import BeautifulSoup
import time

start_time = time.time()

courseCodes = ("AFRS", "AMCL", "AMST", "ANSO", "ANTH", "AFRS", "ART", "ARTH", "ARTS", "ASIA", "ASL", "ASTR", "BIOC", "BIOL", "BIPS", "CHEM", "CHIN", "CHJA", "CLAN", "CLAS", "CLGR", "CLLA", "CLCS", "CMPU", "COGS", "CREO", "DANC", "DRAM", "ECON", "EDUC", "ENGL", "ENST", "ENVI", "ESCI", "ESSC", "FFS", "FILM", "FREN", "GEAN", "GEOG", "GEOL", "GERM", "GREK", "GRST", "HEBR", "HIND", "HISP", "HIST", "INDP", "INTD", "INTL", "IRSH", "ITAL", "JAPA", "JWST", "ASIA", "LALS", "LAST", "LATI", "MATH", "MEDS", "MRST", "MSDP", "MUSI", "NEUR", "PERS", "PHED", "PHIL", "PHYS", "POLI", "PORT", "PSYC", "PSYC", "RELI", "RUSS", "SOCI", "STS", "SWAH", "SWED", "TURK", "URBS", "VICT", "WMST", "YIDD")

#Extracts the HTML file from AskBanner
def genScheduleFile():
    headers = {"Referer": "https://aisapps.vassar.edu/cgi-bin/geninfo.cgi",
               "Origin": "https://aisapps.vassar.edu",
               "Content-Type": "application/x-www-form-urlencoded",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15"}

    payload = {"MIME Type": "application/x-www-form-urlencoded",
               "session": "202003",
               "dept": "",
               "instr": "",
               "type": "",
               "day": "",
               "time": "",
               "unit": "",
               "format": "",
               "submit": "Submit"}

    f = requests.post("https://aisapps.vassar.edu/cgi-bin/courses.cgi", data=payload, headers=headers)
    schedule = open('scheduleOfClasses.txt', 'w')
    schedule.write(f.text)
    #print(f.text, file=schedule)
    schedule.close()

def removeTags():
    scheduleReader = open('scheduleOfClasses.txt', 'r')
    soup = BeautifulSoup(scheduleReader, 'lxml')
    scheduleReader.close()
    courseEntry = soup.get_text()
    parsedFile = open('parsedFile.txt', 'w')
    parsedFile.write(courseEntry)
    parsedFile.close()

class Course:
    inputLn = ""
    values = [None] * 30

    #Fields with prereg requests: 
    fields = ("requests", "limits", "courseID", "title", "units", "sp", "max", "enr", "avl", "wl", "gm", "yl", "pr", "fr", "la", "qa",
              "format", "xlist", "d1", "time1", "d2", "time2", "loc", "instructor", "starttime1", "duration1", "delt91"
              "starttime2", "duration2", "delt92") # 30 elements
    fieldPos = [0, 9, 13, 26, 57, 63, 66, 70, 74, 78, 82, 87, 90, 93, 96, 99, 102, 109, 125, 131, 146, 131, 146, 158] #length=24
    #           0  1  2    3  4   5   6   7   8   9   10  11  12  13  14  15  16   17    18   19   20   21   22   23
 
    def __init__(self, inputLine):
        self.inputLn = inputLine

    def scheduleReader(self):
        #reset values
        for i in range (0,30): 
            self.values[i] = None
        # when characters 0 to 9 are blank, the line is a line for the class' second day
        if self.inputLn[0:9].strip()=='': 
            self.values[18]=(self.inputLn[112:116]).strip()
            self.values[19]=(self.inputLn[118:131]).strip()

        else: #non blank 
            if '-' in self.inputLn[0:9]: #course limits present
                fieldPos_limits = [0, 0, 0, 13, 44, 50, 53, 57, 61, 65, 69, 74, 77, 80, 83, 86, 89, 96, 112, 118, 133, 118, 133, 145] #length=24                                     
                for i in range(2, 24): 
                    if i == 20 or i == 21: # skip over the d2 time2 fields
                        continue
                    elif i < 23:
                        self.values[i] = self.inputLn[fieldPos_limits[i]:fieldPos_limits[i + 1]]
                    else:  #if i = 23, read until the end of the line
                        self.values[i] = self.inputLn[fieldPos_limits[i]:]
                    self.values[i] = self.values[i].strip()
                    if i == 4 and self.values[i] != "": 
                        self.values[i] = Decimal(self.values[i])
                    # handles the course features like QA, FW, LA, etc. Set value to 1 if present, 0 otherwise
                    if i == 5 or i == 11 or i == 12 or i == 13 or i == 14 or i == 15:
                        if self.values[i] != "":
                            self.values[i] = 1
                        else:
                            self.values[i] = 0

            elif '/' in self.inputLn[0:9]: 
                self.values[1]=self.inputLn[0:12].rstrip()
            else: #course limits not present, only number of requests
                reqNumber = self.inputLn[0:9]
                if reqNumber != '' and ('F' not in reqNumber) and ('S' not in reqNumber): # avoid the lines with "Fall" or "Spring"
                    self.values[0]=int(reqNumber.strip())
        
        if self.values[19] and not ('0000' in self.values[19]) and ('AM' in self.values[19] or 'PM' in self.values[19]): # if self.values[19] holds time values
                # starttime1:
                if self.values[19][4:6] == 'AM' or self.values[19][0:2]=='12': # Banner lists PM time as 0100PM. Time before 1pm is correct
                    self.values[24] = int(self.values[19][0:4])
                else:
                    self.values[24] = 1200 + int(self.values[19][0:4])

                starttime1 = self.values[24]
                # convert the string into time-type data (start time and end time)
                time_starttime1 = datetime(year=2020, month=1, day=1, hour=int(starttime1 / 100),
                                        minute=int(starttime1 % 100), second=0)
                if self.values[19][11:13] == 'AM' or self.values[19][7:9]=='12':
                    endtime1 = int(self.values[19][7:11])
                else:
                    endtime1 = 1200 + int(self.values[19][7:11])
                time_endtime1 = datetime(year=2020, month=1, day=1, hour=int(endtime1 / 100),
                                        minute=int(endtime1 % 100), second=0)
                # calcualte duration in minutes
                self.values[25] = time_endtime1 - time_starttime1
                self.values[25] = int(self.values[25].total_seconds() / 60)
                # calculate how far start time is from 9am
                self.values[26] = time_starttime1 - datetime(year=2020, month=1, day=1, hour=9, minute=0, second=0)
                self.values[26] = float((self.values[26].total_seconds()/60)/60)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Courses.objects.all().delete()
        # Courses.objects.raw('TRUNCATE table search_courses')
        genScheduleFile()
        removeTags()
        rawFile = open("parsedFile.txt", "r")
        print("Completed parsing")
        preRegRequests = 0
        courseIDPrev=""
        courseLimits=""
        for line in rawFile:
            # skip all the non-class lines
            if "Course Listings" in line or "Supplement to the Schedule of Classes" in line or "Course listings for Fall 2020:" in line or "COURSE ID " in line or "----" in line or "Pre Reg  Class Limits" in line or "Requests SR/JR/SO/FR" in line :
                continue
            else:
                course = Course(line)
                course.scheduleReader()
                courseIDData = course.values[2]
                
                if course.values[0] != '' and course.values[0] != 'F' and course.values[0] != 'S' and course.values[0] is not None:
                    preRegRequests=course.values[0]
                elif course.values[1] is not None and '/' in course.values[1]:
                    courseLimits=course.values[1]
                else: 
                    if courseIDData is not None and courseIDData != "": # this line contains the full course listing
                        print(courseIDData)
                        if courseIDData[3] == "-" or courseIDData[4] == '-':
                            courseIDPrev = course.values[2]
                            try: # check to see if the course already exists
                                updateFields=True
                                c = Courses.objects.get(courseID=course.values[2])
                            except ObjectDoesNotExist:
                                updateFields=False
                                c=Courses()
                            c.requests=preRegRequests
                            c.limits=courseLimits
                            c.title=course.values[3]
                            c.units=course.values[4]
                            c.sp=course.values[5]
                            c.Max=course.values[6]
                            c.enr=course.values[7]
                            c.avl=course.values[8]
                            c.wl=course.values[9]
                            c.gm=course.values[10]
                            c.yl=course.values[11]
                            c.pr=course.values[12]
                            c.fr=course.values[13]
                            c.la=course.values[14]
                            c.qa=course.values[15]
                            c.Format=course.values[16]
                            c.xlist=course.values[17]
                            c.d1=course.values[18]
                            c.time1=course.values[19]
                            c.d2=course.values[20]
                            c.time2=course.values[21]
                            c.loc=course.values[22]
                            c.instructor=course.values[23]
                            c.starttime1=course.values[24]
                            c.duration1=course.values[25]
                            if course.values[26] is not None:
                                c.delt91=((course.values[26]*40)+47) # arithmetic for scheudler placement
                            c.starttime2=course.values[27]
                            c.duration2=course.values[28]
                            if course.values[29] is not None:
                                c.delt92=((course.values[29]*40)+47)
                            if updateFields:
                                # update all fields except the description and courseID (primary key) fields
                                c.save(update_fields=['requests', 'limits', 'title', 'units', 'sp', 'Max', 'enr', 'avl', 'wl', 'gm', 'yl', 'pr', 'fr', 'la', 'qa', 'Format', 'xlist', 'd1', 'time1', 'd2', 'time2', 'loc', 'instructor', 'starttime1', 'duration1', 'delt91', 'starttime2', 'duration2', 'delt92'])
                            else:
                                # insert new row
                                c.courseID=course.values[2]
                                c.save()
                            courseLimits=""

                    else: # this line only contains the d2 and t2 values
                        d2Value = course.values[18]
                        # update the startime2, duration2 and delt92 fields
                        if d2Value is not None and ("M" in d2Value or "T" in d2Value or "W" in d2Value or "R" in d2Value or "F" in d2Value):
                            t2Value = course.values[19]

                            if "PM" in t2Value or "AM" in t2Value:
                                if "-" in t2Value:
                                    if t2Value[4:6] == 'AM' or t2Value[0:2]=='12':
                                        starttime2 = int(t2Value[0:4])
                                    else:
                                        starttime2 = 1200 + int(t2Value[0:4])

                                    time_starttime2 = datetime(year=2020, month=1, day=1, hour=int(starttime2 / 100),
                                                            minute=int(starttime2 % 100), second=0)
                                    if t2Value[11:13] == 'AM' or t2Value[7:9]=='12':
                                        endtime2 = int(t2Value[7:11])
                                    else:
                                        endtime2 = 1200 + int(t2Value[7:11])

                                    time_endtime2 = datetime(year=2020, month=1, day=1, hour=int(endtime2 / 100),
                                                            minute=int(endtime2 % 100), second=0)

                                    duration2 = time_endtime2 - time_starttime2
                                    duration2= int(duration2.total_seconds() / 60)

                                    deltnine2 = time_starttime2 - datetime(year=2020, month=1, day=1, hour=9, minute=0, second=0)
                                    deltnine2 = float((deltnine2.total_seconds()/60)/60)
                                    deltnine2 = (deltnine2*40)+47

                                    clast=Courses.objects.get(courseID=courseIDPrev)
                                    clast.d2=course.values[18]
                                    clast.time2=course.values[19]
                                    clast.starttime2=starttime2
                                    clast.duration2=duration2
                                    clast.delt92=deltnine2
                                    clast.save(update_fields=['d2', 'time2', 'starttime2', 'duration2', 'delt92'])
        print(time.time() - start_time, "seconds")
