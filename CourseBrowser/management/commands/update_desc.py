from django.core.management import BaseCommand
from CourseBrowser.models import Courses
import urllib.request
import ssl
from bs4 import BeautifulSoup
import time

start_time = time.time()

courseCodes = ("AFRS", "AMCL", "AMST", "ANSO", "ANTH", "AFRS", "ART", "ARTH", "ARTS", "ASIA", "ASL", "ASTR", "BIOC", "BIOL", "BIPS", "CHEM", "CHIN", "CHJA", "CLAN", "CLAS", "CLGR", "CLLA", "CLCS", "CMPU", "COGS", "CREO", "DANC", "DRAM", "ECON", "EDUC", "ENGL", "ENST", "ENVI", "ESCI", "ESSC", "FFS", "FILM", "FREN", "GEAN", "GEOG", "GEOL", "GERM", "GREK", "GRST", "HEBR", "HIND", "HISP", "HIST", "INDP", "INTD", "INTL", "IRSH", "ITAL", "JAPA", "JWST", "ASIA", "LALS", "LAST", "LATI", "MATH", "MEDS", "MRST", "MSDP", "MUSI", "NEUR", "PERS", "PHED", "PHIL", "PHYS", "POLI", "PORT", "PSYC", "PSYC", "RELI", "RUSS", "SOCI", "STS", "SWAH", "SWED", "TURK", "URBS", "VICT", "WMST", "YIDD")

def addBlank():
    c = Courses()
    c.courseID="blank"
    c.title="blank"
    c.units=0.0
    c.sp=0
    c.Max=0
    c.enr=0
    c.avl=0
    c.wl=0
    c.gm="NR"
    c.yl=0
    c.pr=0
    c.fr=0
    c.la=0
    c.qa=0
    c.Format="CLS"
    c.xlist="blank"
    c.d1="M"
    c.time1="blank"
    c.d2="M"
    c.time2="blank"
    c.loc="blank"
    c.instructor="blank"
    c.starttime1=0
    c.duration1=0
    c.delt91=0
    c.starttime2=0
    c.duration2=0
    c.delt92=0
    c.requests=0
    c.limits="blank"
    c.save()

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Updating description...")
        # to avoid urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1108)>
        ssl._create_default_https_context = ssl._create_unverified_context
        global courseCodes
        for i in range(1, 23):
            # iterate over page numbers
            urlData ="https://catalogue.vassar.edu/content.php?filter%5B27%5D=-1&filter%5B29%5D=&filter%5Bcourse_type%5D=-1&filter%5Bkeyword%5D=&filter%5B32%5D=1&filter%5Bcpage%5D=" + str(i) + "&cur_cat_oid=39&expand=1&navoid=7049&print=1#acalog_template_course_filter"
            # open the url
            webUrl = urllib.request.urlopen(urlData)
            data = webUrl.read().decode("utf-8")
            # create beautiful soup object soup for each webpage
            soup = BeautifulSoup(data, "lxml")
            # trFile to save all the tr blocks in the body
            trFile = open('trFile.txt', 'w+')
            for string in soup.body.find_all('tr'):
                # print each tr line to a trFile
                print(repr(str(string)), file=trFile)
            trFile.close()
            trFileReader = open("trFile.txt", "r")
            for line in trFileReader:
                # create a new BeautifulSoup object soupTr to extract the text in each line in the trFile
                soupTr = BeautifulSoup(line, "lxml")
                # extract the text
                courseEntry = soupTr.get_text()
                # remove the character sequence \xa0
                courseEntry = courseEntry.replace(r"\xa0\xa0", ' ')
                courseEntry = courseEntry.replace(r"\xa0", '')
                courseInfo = [None] * 3
                courseCode = courseEntry[22:26].strip()
                # print(courseCode)
                if not (courseCode in courseCodes):
                    continue
                courseInfo[0] = courseCode
                courseInfo[1] = courseEntry[27:30].strip()
                courseInfo[2] = courseEntry[courseEntry.find("unit(s)") + 7:].replace(r"\n", " ").rstrip(r"'").strip()
                courseInfo[2] = courseInfo[2][:-2]
                # print(courseInfo)
                for c in Courses.objects.filter(courseID__icontains=courseInfo[0]).filter(courseID__icontains=courseInfo[1]):
                    c.description=courseInfo[2]
                    c.save()
        print("Adding blank line...")
        addBlank()
        print(time.time() - start_time, "seconds")
