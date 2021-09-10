from selenium                                import webdriver
from selenium.webdriver.common.by            import By
from selenium.webdriver.support.ui           import WebDriverWait
from selenium.webdriver.support              import expected_conditions as EC

from tkinter import *
import threading
import os
import re
import time


class AzDriver:
    def __init__(self,master):
        global amazon_url
        #self.amazon_url = amazon_url
        self.root = master
        self.skipper = True
        
        
        self.calc_frame = Frame(self.root,background='cyan3',padx=2,pady=2)
        self.calc_frame.pack()
        
        self.label6 = Entry(self.calc_frame,text='amazPrice', textvariable="amazPrice", justify = CENTER, borderwidth=2, width = 7,fg = "snow", bg = "aquamarine4",)
        self.label6.insert(0, "AZPrice")
        self.label6.pack(side="left", fill="y")
        
        self.label7 = Entry(self.calc_frame,text='ebayPrice', textvariable="ebayPrice", justify = CENTER, borderwidth=2, width = 7,fg = "snow", bg = "aquamarine4",)
        self.label7.insert(0, "EBPrice")
        self.label7.pack(side="left", fill="y")
        
        self.label8 = Label(self.calc_frame,text='Profit:',  justify = CENTER, borderwidth=1, width = 7,fg = "black", bg = "cyan3",)
        self.label8.pack(side="left", fill="y")
        
        self.profit_entry = Entry(self.calc_frame,text='profit', justify = CENTER, borderwidth=2, width = 7,fg = "snow", bg = "aquamarine4",)
        self.profit_entry.insert(0, "X")
        self.profit_entry.pack(side="left", fill="y")
        
        self.store_label = Label(self.calc_frame,text='Store:',  justify = CENTER, borderwidth=1, width = 7,fg = "black", bg = "cyan3",)
        self.store_label.pack(side="left", fill="y")
        
        self.store_entry = Entry(self.calc_frame,text='Store', justify = CENTER, borderwidth=2, width = 7,fg = "snow", bg = "aquamarine4",)
        self.store_entry.insert(0, "X")
        self.store_entry.pack(side="left", fill="y")
        
        self.button_calc = Button(self.calc_frame,command = self.calcualate_funct, text = "CALCULATE",padx = 1, pady=1, borderwidth=2,fg = "snow", bg = "gray25")
        self.button_calc.pack(side="left", fill="y")
        
        self.button_az = Button(self.calc_frame, text = "AMZ",padx = 10, pady=1, borderwidth=2, width =6,fg = "snow", bg = "gray25", command = self.browser_thread)
        self.button_az.pack(side="left", fill="y")

    def change_url(self,val):
        global amazon_url
        amazon_url = val
        self.calc_funct_update("0","0","0","X")
        self.browser_thread()
        
        #print(amazon_url)

    def close_browser(self):
        self.driver.close()
        
        
    def calc_funct_update(self,ap,ep,pr,store):
        if ap:
            self.label6.delete(0, END)
            self.label6.insert(0, ap)
        if ep:
            self.label7.delete(0, END)
            self.label7.insert(0, ep)
        if pr:
            self.profit_entry.delete(0, END)
            self.profit_entry.insert(0, pr)
        if store:
            self.store_entry.delete(0, END)
            self.store_entry.insert(0, store)
            
        
    def calc_funct_return(self):
        x = self.profit_entry.get()
        E = self.label7.get()
        try:
            e = (re.findall("\d+\.\d+", E)[0])
        except:
            e = self.label7.get()
        store = self.store_entry.get()
#        self.profit_entry.delete(0, END)
#        self.label6.delete(0, END)
#        self.label7.delete(0, END)
        return [e,x,store]

    def calcualate_funct(self):
        try:
            a = float(self.label6.get())
            try:
                E = self.label7.get()
                e = float(re.findall("\d+\.\d+", E)[0])
            except Exception as e:
                print(e)
                e = float(self.label7.get())
            x = round((a-(a*0.15)-e),2)
            self.calc_funct_update("","",x,"")

        except:
            self.calc_funct_update("ERROR","ERROR","ERROR","")
#            self.label6.delete(0, END)
#            self.label6.insert(0, "ERROR")
#            self.label7.delete(0, END)
#            self.label7.insert(0, "ERROR")

    def open_browser(self):
        global amazon_url
        
        try:
            sys_username = str(os.getenv('username'))
            options = webdriver.ChromeOptions()
            # TELL WHERE IS THE DATA DIR
            options.add_argument(r"--user-data-dir=C:\Users\{0}\AppData\Local\Google\Chrome\User Data\Profile {0}".format(
                sys_username))
            # USE THIS IF YOU NEED TO HAVE MULTIPLE PROFILES
            options.add_argument('--profile-directory=Profile {0}'.format(sys_username))
    
     
            self.driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
            self.driver.implicitly_wait(1) 
            
            self.driver.get(amazon_url)
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR , 'div[id="sc-logo-top"]'))
                )
                #print(element.get_attribute('innerHTML'))
            except:
                print('AZ_login seq activated')
                self.AZ_login(self.driver)
            return self.driver
        except Exception as e:
            print(e)
        finally:
            time.sleep(1)
            self.button_az['state'] = 'active'
            self.skipper = True
            

    def navigate_browser(self,driver):
        global amazon_url
        print(amazon_url)
        self.driver = driver
        self.driver.get(amazon_url)
        try:
            X = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR , 'table[class="a-normal a-spacing-micro"]'))
            )
            
#            print(X.get_attribute('innerHTML'))
#            print(X.text)
            X = X.text
            amazon_sold = (re.findall("\d+\.\d+", X)[0])
            self.label6.delete(0, END)
            self.label6.insert(0, amazon_sold)
        except Exception as e:
            print('Amazon Price not scraped:',e)
        finally:
            self.button_az['state'] = 'active'
            self.skipper = True
        #driver.quit()
        
    def browse_az(self):
        global amazon_url
        self.button_az['state'] = 'disabled'
        
        if self.skipper == True:
            self.skipper = False
            try:
                assert amazon_url != '' or amazon_url != None
            except:
                amazon_url = "https://sellercentral.amazon.com/order-reports-and-feeds/reports/unshippedOrders#"
            try:
                #navigate to current URL
                
                self.navigate_browser(self.driver)
            except:
                #open new webDriver if none
                
                self.driver = self.open_browser()
        
        
    def browser_thread(self):

        th = threading.Thread(target=self.browse_az)
        th.start()

    def AZ_login(self,driver_amz):#with wait for double conf

        try:
            lnk = "https://sellercentral.amazon.com/gp/sign-in/logout.html/ref=xx_logout_dnav_xx"
            driver_amz.get(lnk)
        except:
            pass
    
        link = (f'https://sellercentral.amazon.com/signin') 
        driver_amz.get(link)
        driver_amz.implicitly_wait(1)
        
        email = 'censored@gmail.com'
        password = 'censored'
        
        css_selector = driver_amz.find_element_by_css_selector
        
        try:
            acc_field = WebDriverWait(driver_amz, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR , 'input[type="email"]'))
                    )
            #acc_field = css_selector('input[type="email"]')
            acc_field.send_keys(str(email))
        
        except:
            pass
        acc_field = WebDriverWait(driver_amz, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR , 'input[type="password"]'))
                    )
        #acc_field = css_selector('input[type="password"]')
        acc_field.send_keys(str(password))
        
        keep_signed = css_selector('input[name="rememberMe"]')
        keep_signed.click()
        sign_in = css_selector('input[id="signInSubmit"]')
        sign_in.click()
        
        try:
            WebDriverWait(driver_amz, 100).until(
                EC.presence_of_element_located((By.CSS_SELECTOR , 'div[id="sc-logo-top"]'))
            )
            #print(element.get_attribute('innerHTML'))
        except:
            print('AZ_login amazon unconfirmed')








