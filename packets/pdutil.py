import pandas as pd
import os
import sqlite3 as lite


def find_txt_files_list(directory):
    '''returns a txt_file_list for the current directory'''
    directory
    txt_file_list = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            txt_file_list += [(os.path.join(directory, file))]
    
    return txt_file_list





def pandas_magick(directory,old_orders_csv):
    '''takes a txt tab deliminated file as arg and 
        returns a dict:
        {'col_keys':column_keys,'iter_data':iterable_data,}
        
        DataFrame.at[index,col_name] = '112-3942081-testtest' #sets data in to cell
        x = DataFrame.at[index,col_name] #gets data from cell
        len(DataFrame.index)
    '''
    if old_orders_csv:
        pass
    else:
        old_orders_csv = 'old orders.csv'
    #i - index that chooses txt file from the list
    i = 0
    
    txt_file = find_txt_files_list(directory)[i]
    #print(txt_file, f'- curently set to element {i}')

    if txt_file:

        path_old_orders = (os.path.join(os.path.dirname(txt_file), old_orders_csv))
        #print(path_old_orders)
           
        data = pd.read_csv(txt_file, sep="\t")
        old_orders_data = pd.read_csv(path_old_orders, sep=",")
        
        
        
        delete_col_list = ['order-item-id','purchase-date','payments-date',
                           'reporting-date' ,'promise-date','buyer-email',
                           'product-name','quantity-shipped','price-designation',
                           'purchase-order-number','is-business-order','ship-country',
                           
                           ]
        
        delete_col_list_old = ['D/O','EMAIL','Pass','PP','PROFIT','DAY TOTAL','STORE','QTY','Name','Tracking','OTC']
        # drop deletes the columns of the dataFrame
        # use index='1' to delete 1 row
        
        
        
        for col in delete_col_list:
            try:
                data.drop( columns=col , inplace=True)
            except:
                print(f'Exception in "pandas_magick(txt_file)": column {col} not found')
        
        
        
        old_orders_data_copy = old_orders_data.rename(columns={'ID': 'order-id',}, inplace=False)
        for col in delete_col_list_old:
            try:
                old_orders_data_copy.drop( columns=col , inplace=True)
            except:
                print(f'Exception in "pandas_magick(txt_file)": column {col} not found')

        new_orders = (pd.merge(data,old_orders_data_copy, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1))

        #column_keys = data.columns.values
        #data = data.to_numpy()
        if new_orders.empty:
            print('--EMPTY DF')
        else:
            print('--DATA LOADED')

        return {
                'new_orders':new_orders,
                'old_orders':old_orders_data,
                }
    else:
        print("order txt not found")


#---------------------------------------------------------------------------------------


def get_pps(full_directory):
    file_name = 'paypal.csv'
    file_dir = (os.path.join(full_directory, file_name))
    with open (file_dir,'r') as f:
        data = f.read()

    return data.split('\n')


def get_item_details(SKU):
    user = str(os.getenv('username'))
    directory = f'C:\\Users\\{user}\\Desktop\\'#Clean Inventory v11'
    for file in os.listdir(directory):
        if file.startswith('Clean Inventory'):
            DB_folder = file
    
    DB = os.path.join(DB_folder, 'data\\DB_path.txt')
    directory = os.path.join(directory, DB)
    #print(directory)
    with open(directory, 'r') as save_file:
        DB_path = save_file.readline()
        #print(DB_path)
        result = None
        
        SKU = SKU.replace(';',"' OR SKU = '")

        #connecting to INVENTORY DATABASE
        try:
            con = lite.connect(DB_path)
            cur = con.cursor()
            cur.execute(f"""SELECT UPC FROM items WHERE SKU = '{SKU}'""")
            new = []
            result = cur.fetchall()
            for item in result:
                new += item
            result =  new
            #con.commit()
        except Exception as e:
            print(e)
        finally:
            if con:
                con.close()
    return result


def get_mail(full_directory):
    '''
    reads mail csv, gets one mail, ads a use counter and rewrits the csv.
    
    return ['EMAIL','Pass']
    '''
    file_name = 'mails.csv'
    file_dir = (os.path.join(full_directory, file_name))
    data = pd.read_csv(file_dir, sep=",")
    data = data.sort_values(by=['Used'])
    
    try:
        new_val = int(data.at[0,'Used'])+1
        data.at[0, 'Used'] = new_val
    except Exception as e:
        print(e)
        
    data = data.sort_values(by=['Used'])  
    data.to_csv(file_dir, index=False , encoding = 'utf-8')
    
    mali = data.at[0,'EMAIL']
    password = data.at[0,'Pass']

    return [mali,password]


if __name__ == "__main__":
    '''
    pandas_data = pandas_magick('.','')
    new_orders = pandas_data['new_orders']
    old_orders = pandas_data['old_orders']
    
    print(new_orders.to_numpy())
    
    
    for row in old_orders.head().index: 
        print(row, end = " ") 
    
    #get mail
#    x = (get_mail('.'))
#    print(x)
    
    
    #get paypal
    c = get_pps('.')
    print('\n\n',c)
    '''
    test_order_ids = '2T-8REP-IN6O;I4-EXY4-55TI;CR-WEA0-CHGV'
    x = get_item_details(test_order_ids)
    print(x)
        
        