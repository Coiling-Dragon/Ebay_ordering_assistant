# -*- coding: utf-8 -*-
"""
Created on Thu May 14 15:39:37 2020

@author: CoilingDragon

if (changes in SOLD sheets format) - 236 row
#if problems with orders or changes in orders txt headers: - 81 row
"""
# from win32api import GetKeyState
# import threading
# import time

from packets.keylog import KeyLogger
from packets.azdriver import AzDriver
from packets.pdutil import pandas_magick, get_mail, get_pps, get_item_details
from extractor.order_extractor import source

from tkinter import *
import threading
import os
import pandas as pd
import numpy as np
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MainProgram:

    def __init__(self):
        self.root = Tk()
        self.root.attributes("-topmost", True)
        self.root.configure(background='cyan4')
        self.root.geometry("440x220")
        self.root.resizable(False, True)

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DATA_DIR = self.path_finder()
        print(self.DATA_DIR)

        # initiate paypals
        self.pps_list = get_pps(self.DATA_DIR)

        self.count_order = -1
        self.all_orders_count = 0

        self.order_data_list = []
        self.mails_list = []
        self.data_to_be_stored = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ]

        self.KeyLogger_funct = KeyLogger(self.root)

        self.buttons_funct()
        self.create_lable_funct()

        self.az_funct = AzDriver(self.root)

        self.l3, self.l4, = 'no orders data', 'no orders data'

    def get_orders(self):
        source(self.DATA_DIR)

    def init_pandas(self):

        pandas_data = pandas_magick(self.DATA_DIR, 'old orders.csv')

        if pandas_data:

            self.old_order_dataFrame = pandas_data['old_orders']
            self.order_data_list = pandas_data['new_orders'].to_numpy(dtype=str)
            self.order_header_list = (pandas_data['new_orders'].columns.values.tolist())

            self.all_orders_count = len(self.order_data_list)

            if self.all_orders_count == 0:
                self.l3 = 'NO NEW ORDERS'
                self.l4 = 'NO NEW ORDERS'
                self.update_l3_l4_l5_funct()

            '''
            #if problems with orders or changes in orders txt headers:
            print(self.order_header_list)
            print('Today Orders:',len(self.order_data_list))
            print (self.order_data_list[0])
            '''

        else:
            self.l3 = 'pandas_magick(self.DATA_DIR) - empty'
            self.l4 = 'pandas_magick(self.DATA_DIR) - empty'
            self.update_l3_l4_l5_funct()

    def write_order_csv(self):
        try:
            if self.old_order_dataFrame.empty:
                pass
            else:
                self.DATA_DIR
                try:
                    self.next_order()
                except:
                    pass
                # print(self.old_order_dataFrame.columns.values.tolist())
                path_old_orders = (os.path.join(self.DATA_DIR, 'old orders.csv'))
                self.old_order_dataFrame.to_csv(path_old_orders, index=False)

                self.l4 = path_old_orders
                self.l3 = 'old orders csv saved in path:'

                try:
                    self.update_l3_l4_l5_funct()
                except:
                    pass
        except Exception as e:
            print(e)

    def compose_addres(self, count_order):
        try:
            assert self.mails_list[count_order][0]
            assert self.mails_list[count_order][1]
            mail_to_use = self.mails_list[count_order]
        except:
            self.mails_list += [get_mail(self.DATA_DIR)]
            mail_to_use = self.mails_list[count_order]
            print("\n\n", mail_to_use, "\n\n")

        # need to add paypal data to current_order_data
        current_order_data = np.append(self.order_data_list[count_order], mail_to_use)
        current_order_header = self.order_header_list + ['MAIL', 'PASS']

        current_order_dict = {}
        c = 0
        for info in current_order_data:
            # createing dictionary with kay val pairs
            current_order_dict[current_order_header[c]] = info
            c += 1

        self.current_order_dict = current_order_dict
        '''
        print(current_order_dict)
        ields:
        ['order-id', 'days-past-promise', 'buyer-name', 'buyer-phone-number', 'sku', 
        'quantity-purchased', 'quantity-to-ship', 'ship-service-level', 'recipient-name', 
        'ship-address-1', 'ship-address-2', 'ship-address-3', 'ship-city', 'ship-state', 
        'ship-postal-code','MAIL','PASS','buyer-name-1','buyer-name-2']
        
        '''

        buyer_name = current_order_dict['recipient-name']
        buyer_name_1 = buyer_name.split()[0]
        buyer_name_2 = ' '.join(buyer_name.split()[1:])
        current_order_dict['buyer-name-1'] = buyer_name_1
        current_order_dict['buyer-name-2'] = buyer_name_2

        upc = '<--->'.join(get_item_details(current_order_dict['sku']))

        if current_order_dict['ship-address-2'] == 'nan':
            current_order_dict['ship-address-2'] = ''
        if current_order_dict['ship-address-3'] == 'nan':
            current_order_dict['ship-address-3'] = ''
        addres2 = (' '.join([current_order_dict['ship-address-2'], current_order_dict['ship-address-3']]))

        # ----------------------export data list to keyLogger

        data_to_be_passed = []
        data_to_be_passed.append(current_order_dict['buyer-name-1'])
        data_to_be_passed.append(current_order_dict['buyer-name-2'])
        data_to_be_passed.append(current_order_dict['ship-address-1'])

        data_to_be_passed.append(addres2)
        data_to_be_passed.append(current_order_dict['ship-city'])
        data_to_be_passed.append(current_order_dict['ship-state'])

        data_to_be_passed.append(current_order_dict['ship-postal-code'])
        data_to_be_passed.append(current_order_dict['MAIL'])
        data_to_be_passed.append(current_order_dict['MAIL'])

        data_to_be_passed.append(current_order_dict['buyer-phone-number'])

        self.amazon_url = "https://sellercentral.amazon.com/orders-v3/order/" + current_order_dict['order-id']
        self.az_funct.change_url(self.amazon_url)

        self.KeyLogger_funct.pass_order_data(data_to_be_passed, current_order_dict)

        # ----------------------store data list

        data_to_be_stored = []

        # 0
        data_to_be_stored.append(current_order_dict['order-id'])

        # 1
        data_to_be_stored.append(datetime.datetime.now().strftime('%m/%d'))

        # 2
        data_to_be_stored.append(current_order_dict['MAIL'])

        # 3
        data_to_be_stored.append(current_order_dict['PASS'])

        # 4
        data_to_be_stored.append('')  # -------paypal

        # 5
        data_to_be_stored.append('')  # -------profit

        # 6
        data_to_be_stored.append('')  # -------DAY TOTAL

        # 6 -7
        data_to_be_stored.append('')  # -------store

        # 7 - 8
        data_to_be_stored.append(current_order_dict['quantity-to-ship'])

        # 8 -9
        data_to_be_stored.append('')  # -------name

        # 9 -10
        data_to_be_stored.append('')  # -------track

        # 10 - 11
        data_to_be_stored.append('')  # -------cost to aquire

        self.data_to_be_stored = data_to_be_stored
        # ----------------------store data list

        self.l3 = (' ] [ '.join(
            [(str(self.count_order + 1) + '/' + str(self.all_orders_count)), current_order_dict['order-id'], ]))
        self.l4 = upc

    def append_new_to_old_orders(self):
        # get calculated data for current order
        calculated_data = self.az_funct.calc_funct_return()
        self.data_to_be_stored[11] = calculated_data[0]
        self.data_to_be_stored[5] = calculated_data[1]
        self.data_to_be_stored[7] = calculated_data[2]

        # get the paypal too
        paypal = self.v.get()

        PPLvalues_inverted = {y: x for x, y in self.PPLvalues.items()}
        self.data_to_be_stored[4] = PPLvalues_inverted[paypal]

        '''
        #if problems occour eneble those prints - (changes in SOLD sheets format)
        print(self.data_to_be_stored)
        print(len(self.data_to_be_stored))
        '''

        # append to dataframe
        # self.old_order_dataFrame
        if len(self.data_to_be_stored) == 12:
            new_entry = {}
            c = 0

            for info in self.data_to_be_stored:
                # createing dictionary with kay val pairs
                new_entry[self.old_order_dataFrame.columns.values.tolist()[c]] = info
                c += 1

            self.old_order_dataFrame.loc[len(self.old_order_dataFrame)] = new_entry
            self.old_order_dataFrame.drop_duplicates(subset='ID', keep="first", inplace=True)
            '''
            print(new_entry)
            print(self.old_order_dataFrame)
            '''

    def next_order(self):
        self.KeyLogger_funct.stop_btn_click()

        if (self.count_order <= len(self.order_data_list) - 1) and (len(self.order_data_list) > 0):
            if self.count_order == len(self.order_data_list) - 1:
                self.count_order = len(self.order_data_list) - 1
            else:
                self.count_order += 1

            # append data for writeing
            self.append_new_to_old_orders()

            # compose next address
            self.compose_addres(self.count_order)
            self.update_l3_l4_l5_funct()

        else:
            self.l3, self.l4, = 'no orders data', 'no orders data'
            self.update_l3_l4_l5_funct()

    def prev_order(self):
        self.KeyLogger_funct.stop_btn_click()

        if (self.count_order >= 0) and (len(self.order_data_list) > 0):
            self.count_order -= 1
            if self.count_order == -1:
                self.count_order = 0
            #                self.l3,self.l4,self.l5 = 'no orders data', 'no orders data', 'no orders data'
            #                self.update_l3_l4_l5_funct()
            else:
                # append data for writeing
                self.append_new_to_old_orders()

                # compose next address
                self.compose_addres(self.count_order)
                self.update_l3_l4_l5_funct()
        else:
            self.l3, self.l4, = 'no orders data', 'no orders data'
            self.update_l3_l4_l5_funct()

    def create_lable_funct(self):
        entry_width = 78
        self.label3 = Entry(self.root, text='order', textvariable="order", justify=CENTER, borderwidth=2,
                            width=entry_width, fg="snow", bg="aquamarine4", )
        self.label3.insert(0, "# | order id ")
        self.label3.pack()

        self.label4 = Entry(self.root, text='upc', textvariable="upc", justify=CENTER, borderwidth=2, width=entry_width,
                            fg="snow", bg="aquamarine4", )
        self.label4.insert(0, "upc")
        self.label4.pack()

        self.label5 = Entry(self.root, text='email', textvariable="email", justify=CENTER, borderwidth=2,
                            width=entry_width, fg="snow", bg="aquamarine4", )
        self.label5.insert(0, "You can copy paypal from here")
        self.label5.pack()

    def update_l3_l4_l5_funct(self):

        self.label3.delete(0, END)
        self.label3.insert(0, self.l3)
        self.label4.delete(0, END)
        self.label4.insert(0, self.l4)
        self.label5.delete(0, END)
        self.label5.insert(0, self.v.get().replace(',', ' | '))

    def buttons_funct(self):

        self.btn_frame2 = Frame(self.root, background='cyan3', padx=2, pady=2)
        self.btn_frame2.pack()

        self.btn_frame = Frame(self.root, background='cyan3', padx=2, pady=2)
        self.btn_frame.pack()

        self.button_wreadtxt = Button(self.btn_frame, command=self.write_order_csv, text="write data", padx=10, pady=1,
                                      borderwidth=2, width=6, fg="snow", bg="gray25")
        self.button_wreadtxt.pack(side="left", fill="y")

        self.button_wreadtxt = Button(self.btn_frame, command=self.get_orders, text="DW orders", padx=10, pady=1,
                                      borderwidth=2, width=6, fg="snow", bg="gray25")
        self.button_wreadtxt.pack(side="left", fill="y")

        self.button_readtxt = Button(self.btn_frame, command=self.init_pandas, text="get data", padx=10, pady=1,
                                     borderwidth=2, width=6, fg="snow", bg="gray25")
        self.button_readtxt.pack(side="left", fill="y")

        self.button_stop = Button(self.btn_frame, command=self.prev_order, text="<<- Order", padx=10, pady=1,
                                  borderwidth=2, width=6, fg="snow", bg="gray25")
        self.button_stop.pack(side="left", fill="y")

        self.button_next = Button(self.btn_frame, command=self.next_order, text="Order ->>", padx=10, pady=1,
                                  borderwidth=2, width=6, fg="snow", bg="gray25")
        self.button_next.pack(side="left", fill="y")

        self.button = Button(self.btn_frame, command=self.KeyLogger_funct.on_btn_click, text="re/START", padx=10,
                             pady=1, borderwidth=2, width=6, fg="snow", bg="gray25")
        self.button.pack(side="left", fill="y")

        # Dictionary to create multiple buttons 
        self.PPLvalues = {"PPD": self.pps_list[0],
                          "PPM": self.pps_list[1],
                          "PPS": self.pps_list[2],
                          "PPPR": self.pps_list[3],
                          "PPVR": self.pps_list[4],
                          "PPPV": self.pps_list[5],
                          "PPGV": self.pps_list[6],
                          "PPPP": self.pps_list[7],
                          }
        # Loop is used to create multiple Radiobuttons 
        self.v = StringVar(self.root, "0")
        # rather than creating each button separately 
        for (text, value) in self.PPLvalues.items():
            Radiobutton(self.btn_frame2, command=lambda: self.update_l3_l4_l5_funct(), text=text, variable=self.v,
                        value=value, background='cyan3').pack(side="left", ipady=0)
        self.v.set(self.pps_list[0])

    def path_finder(self):
        # =================================================================function_path_finder():
        program_path = os.path.join(self.BASE_DIR, 'data')

        if 'Googledrive' in program_path:
            program_path = os.path.join(
                program_path.split('Googledrive')[0] + 'Googledrive\\Python_Shared\\Order_assist')
        if 'Google Drive' in program_path:
            program_path = os.path.join(
                program_path.split('Google Drive')[0] + 'Google Drive\\Python_Shared\\Order_assist')
        # print(program_path)
        return (program_path)
        # =================================================================

    def main_loop(self):
        self.root.mainloop()
        self.KeyLogger_funct.stop_btn_click()
        self.write_order_csv()
        try:
            self.az_funct.close_browser()
        except:
            pass


main = MainProgram().main_loop()
