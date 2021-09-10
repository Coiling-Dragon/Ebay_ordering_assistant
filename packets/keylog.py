from win32api import GetKeyState
import win32com.client
import win32clipboard
import threading
import time
from tkinter import *


class KeyLogger:
    def __init__(self,master):
        self.root = master
        global stop_threads
        stop_threads = False
        self.shell = win32com.client.Dispatch("WScript.Shell")
        
        self.monitor_frame = Frame(self.root,background='cyan3',padx=2,pady=2)
        self.monitor_frame.pack()
        
        self.label1 = Label(self.monitor_frame, text = "DW orders--->get data",padx = 10, pady=10, borderwidth=2, width =25,fg = "snow", bg = "cyan4",font=("Courier", 11))
        self.label1.pack(side="left", fill="y")
        self.label2 = Label(self.monitor_frame, text = "",padx = 10, pady=10, borderwidth=2, width =35,fg = "snow", bg = "cyan4",font=("Courier", 11))
        self.label2.pack(side="left", fill="y")
        
        
        
    def pass_order_data(self,*args,**kwargs):
        self.my_order_list = args[0]
        self.current_order_dict = args[1]
        self.current_order_dict["sku"] = self.current_order_dict["sku"].replace(';','\n')
        self.change_KeyLogger_label_text(f'DATA READY:\n Buyer:{self.current_order_dict["buyer-name"]}?',f'ITEMS:{self.current_order_dict["sku"]}\nQtity:{self.current_order_dict["quantity-to-ship"]}')
        #print(self.current_order_dict)
        #print(self.my_order_list,"-passed to event handler")

        
    def on_btn_click(self):
        #print("button clicked")
        global stop_threads
        stop_threads = True
        self.in_new_thread()
        
        
    def stop_btn_click(self):
        global stop_threads
        stop_threads = True
        
        
    def key_down(self,key):
        state = GetKeyState(key)
        if (state != 0) and (state != 1):
            return True
        else:
            return False

    def starter(self):
        global stop_threads
        time.sleep(0.05)
        stop_threads = False
        self.t = 0
        s = 0
        while s < 3000:
            if stop_threads:
                self.change_KeyLogger_label_text(f'Clock timed out\nre/START again?','')
                break
            if self.key_down(0x09):
                try:
                    c_tab = str(self.my_order_list[self.t])
                    self.change_KeyLogger_label_text(f'Clipboard info:\n {c_tab}','')
                    
                    self.copy_to_clipboard(c_tab)
                    
                    time.sleep(0.05)
                    if self.t == 5:
                        self.shell.SendKeys(f"{c_tab}")
                    else:
                        self.shell.SendKeys("^v")
                    self.t+=1
                except Exception as e:
                    #print(e)
                    self.copy_to_clipboard('No More Items in List')
                    self.change_KeyLogger_label_text(f'No More data\nSTATE: {self.my_order_list[5]}','')
                    break
                print("TABED")
                time.sleep(0.05)
            s += 1
            #print(s)
            time.sleep(0.05)


    def change_KeyLogger_label_text(self,val_label1,val_label2):
        if val_label1:
            self.label1['text'] = val_label1
        if val_label2:
            self.label2['text'] = val_label2
    
    
    def in_new_thread(self):
        th = threading.Thread(target=self.starter)
        th.start()


    def copy_to_clipboard(self,text):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

    def paste_to_clipboard(self):
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data

