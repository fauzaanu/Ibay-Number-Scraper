from lib2to3.pgen2 import driver
import os
from pickle import NONE
import random
import time
from numpy import number
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common import action_chains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException ,TimeoutException, WebDriverException,ElementNotInteractableException,SessionNotCreatedException 
from selenium.webdriver.common.proxy import Proxy, ProxyType
import tkinter
import re

class IbaySession :
    def __init__ (self, use_proxy=False) :
        """
        Ibay Session initialization
        """
        #Globals for the class that maybe useful across other modules
        #DEFINE ALL IMPORTANT STUFF THAT IBAY MAY CHANGE HERE
        self.baseurl =  str("http://www.ibay.com.mv")
        self.ibay_Search_bar = str(" //input[@name='q'] ")
        self.ibay_next = str('//*/li/a/i[text()="navigate_next"]')
        self.ibay_links  = str('//*[@class="latest-list-item"]/div/div/div/a') #failed
        self.ibay_links_2 = str('//h5/a') #working version
        self.ibay_number_area = str('/html/body/div[4]/div[3]/div[3]/div[1]/div/div[3]/div[1]/table/tbody/tr/td[2]')
       
        
        #setup the proxy
        if use_proxy == True:
            prox = Proxy()
            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = "45.66.238.4:8800"
            prox.socks_proxy = ""
            prox.ssl_proxy = "45.66.238.4:8800"
            capabilities = webdriver.DesiredCapabilities.CHROME
            prox.add_to_capabilities(capabilities)

            #remmeber to remove the executable path here
            self.driver = webdriver.Chrome(desired_capabilities=capabilities,executable_path="C:\Program Files\Google\Chrome\Application\chrome.exe")
        else:
            options = webdriver.ChromeOptions() 
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            # options.add_experimental_option("debuggerAddress","localhost:<remote-port>")

            self.driver = webdriver.Chrome()
        ignored_exceptions = [StaleElementReferenceException,ElementNotInteractableException,SessionNotCreatedException]
        self.wait = WebDriverWait(self.driver,20,ignored_exceptions=ignored_exceptions)

    def HomePage(self):
        """
        Goes to the ibay homepage
        """
        self.driver.get(self.baseurl)

    def SearchIbay(self,terms):
        """
        Searches for a specefic term on ibay
        """
        search_term = str(terms)
        
        try:
            self.HomePage()
            searchbar = self.wait.until(EC.presence_of_element_located((By.XPATH,self.ibay_Search_bar)))
            ActionChains(self.driver).move_to_element(searchbar).click(searchbar).send_keys(search_term).send_keys(Keys.ENTER).perform()
        except Exception as ex:
            print(ex)
            self.driverExit()
        
       
    def driverExit(self,timer=0):
        """
        exits the driver after a timer (or not)
        """
        time.sleep(timer)
        self.driver.close()

    def nextpage(self):
        """
        Goes to the next page should it exist
        """


        #next button cannot be clicked if the screensize is not full  so use tkinter
        self.screen_resize()
        try:
            nextpage_button = self.wait.until(EC.presence_of_element_located((By.XPATH,self.ibay_next)))
            ActionChains(self.driver).move_to_element(nextpage_button).click(nextpage_button).perform()
        except:
            pass
            #one cause could be that there is no next button as it is the end



    def collect_links(self,query=NONE,limit=1):
        """
        collects links present in the page
        """
        if query == NONE:
            pass
        else:
            self.SearchIbay(query)
        try:
            for i in range(limit):
                links_objects = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,self.ibay_links_2)))
                #rlinks = []
                wlinks = []

                for link in links_objects:
                    #print(link)
                    wlinks.append(link.get_attribute('href'))

                
                # Saving the found links list to a file (overwrite)
                with open(f"{query}.txt",'a') as file:
                    for link in wlinks:
                        if "javascript:;" in str(link):
                            continue
                        file.write(link + "\n")

                self.nextpage()
                    
        
            

        except Exception as x:
            print(x.with_traceback)
            pass

        
    def screen_resize(self,WIDTH=0,HEIGHT=0):
        #NOTE MAKING SURE THIS IS NOT THE CAUSE
        #Get the screensize to make it full screen without hardcoding a resolution
        root = tkinter.Tk()
        root.withdraw()
        
        if (WIDTH, HEIGHT) == (0,0):
            WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
        self.driver.set_window_size(WIDTH,HEIGHT)


    def NumberScraper(self,url):
        self.driver.get(url)
        ibay_number_obj = self.wait.until(EC.presence_of_element_located((By.XPATH,self.ibay_number_area)))
        ibay_number = ibay_number_obj.get_attribute('innerHTML')
        # print(ibay_number)
        return ibay_number

    def RunTheNumbers(self,term):
        #:Load the links from the file  to a list - Only for a nessesary use - this wont be used normally
        try:
            content = open(f"{term}.txt",'r')
            readLinks = []

            for line in content:
                readLinks.append(line)


            content.close() #saves some memoru?
        except Exception as e:
            pass

        try:
            for link in readLinks:
                result = self.NumberScraper(link)
                #removing the duplicates from the list by changing to a set and  back to a list
                with open(f"{term} Numbers.txt",'a') as file:   
                    file.write(result + "\n")

        except:
            pass

    def cleanup(self,filename): #Many Supressions of exceptions here - need to fix perheps
        """
        clean up and format the numbers extracted
        """

        #no need of collecting line numbers -
        # phoneNumRegex = re.compile(r'\d\d\d-\d\d\d-\d\d\d\d')
        dhiraagu_numbers = re.compile(r'7\d\d\d\d\d\d')
        ooredoo_numbers = re.compile(r'9\d\d\d\d\d\d')
        numbers = []
        tmpfile = open(f"{filename}",'r')
        for line in tmpfile:
            #print(line)
            Dhiraagu_robj = dhiraagu_numbers.search(line)
            Ooredoo_robj = ooredoo_numbers.search(line)
            try:
                if int(Dhiraagu_robj.group()) > 7000000:            
                    numbers.append(int(Dhiraagu_robj.group()))
                if int(Ooredoo_robj.group()) > 9000000:
                    numbers.append(int(Ooredoo_robj.group()))
            except AttributeError:
                pass
                #print("AttributeError")

        #Removing the duplicates       
        numbers_tmp = list(set(numbers))
        numbers = numbers_tmp
        print(numbers)
        
        # >>> mo = phoneNumRegex.search('My number is 415-555-4242.')
        # >>> print('Phone number found: ' + mo.group())
        # Phone number found: 415-555-4242


if __name__ =="__main__":
    session = IbaySession()
    # session.collect_links("Mobile Phone",limit=5)
    # session.RunTheNumbers(f"Mobile Phone")
    session.cleanup("Mobile Phone Numbers.txt")
    session.driverExit()







#important snippets
    #         # waiting for and closing the notifications dialog
            
    #         possible_buttons = ["Save Info","Turn On"]
    #         dialog = self.wait.until(EC.presence_of_element_located((By.XPATH,self.saveinfo)))
    #         ActionChains(self.driver).move_to_element(dialog).click(dialog).perform()
            

    #         dialog = self.wait.until(EC.presence_of_element_located((By.XPATH,self.turnon)))
    #         dialog = self.wait.until(EC.presence_of_element_located((By.XPATH,self.notnow)))
    #         ActionChains(self.driver).move_to_element(dialog).click(dialog).perform()

# # posts_like_buttons = self.wait.until(
# EC. presence_of_all_elements_located (
# (

    #         # using an action chain to write the username and password
    #         # into the two input fields on the login screen
    #         action_chain = ActionChains(self.driver)
    #         action_chain.move_to_element(username_input).click()
    #         action_chain.send_keys(username)
    #         action_chain.move_to_element(password_input).click()
    #         action_chain.send_keys(password)
    #         action_chain.send_keys(Keys.ENTER)
    #         action_chain.perform()