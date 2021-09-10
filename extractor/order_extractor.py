import os
import mws
import xml.etree.ElementTree as ET
import re
import extractor.g_sheet as sheets
import datetime


def reg_it(text):
    changed = re.findall(r'.+}(\w+)\s*', str(text))
    return changed[0]


def source(path):
    '''
    pip install mws
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    '''
    file_name = 'orders_report.txt'
    file_dir_name = (os.path.join(path, file_name))

    MWS_MARKETPLACE_ID = 'ATVPDKIKX0DER'

    orders_api = mws.Orders(
        access_key='AKIAICYVBSJT74OWYIPA',
        secret_key='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',
        account_id='A61G3C2W760IY')

    service_status = orders_api.get_service_status()

    # Check connection different status types
    # print(service_status.original)
    # print(service_status.parsed)
    # print(service_status.response)

    last_ninety_days = (datetime.datetime.now() - datetime.timedelta(90)).isoformat()
    orders_list = orders_api.list_orders(created_after=last_ninety_days,
                                         marketplaceids=MWS_MARKETPLACE_ID,
                                         orderstatus='Unshipped')
    # View as XML
    orders_as_xml = orders_list.original

    # Write XML file
    with open('ListOrders.xml', 'w', encoding='utf-8') as f:
        f.write(orders_as_xml)

    # Build XML tree and start extracting info
    tree = ET.parse('ListOrders.xml')
    root = tree.getroot()

    # print(f'There are {len(root[0][0])} orders today.')
    orders_dict = {}
    list_of_dict = list()

    # Get a list with orders already in SOLD
    orders_in_sold = sheets.main()

    orders_file_head = 'order-id	order-item-id	purchase-date	payments-date	reporting-date	promise-date	' \
                       'days-past-promise	buyer-email	buyer-name	buyer-phone-number	sku	product-name	' \
                       'quantity-purchased	quantity-shipped	quantity-to-ship	ship-service-level	recipient-name	' \
                       'ship-address-1	ship-address-2	ship-address-3	ship-city	ship-state	ship-postal-code	' \
                       'ship-country	is-business-order	purchase-order-number	price-designation\n'

    with open(file_dir_name, 'w', encoding='utf-8') as f:
        f.write(orders_file_head)

    # root[0][0] stands for ListOrdersResponse(root)->ListOrdersResult[0]->Orders[0][0]
    for order in root[0][0]:
        # print('\n\n\n============ NEXT ORDER ============\n')
        for each in order:
            orders_dict[reg_it(each.tag)] = each.text.strip()
            for sub_each in each:
                orders_dict[reg_it(sub_each.tag)] = sub_each.text.strip()
        # print(orders_dict)

        list_of_dict.append(dict(orders_dict))
        orders_dict.clear()

    line_write = list()
    # Check if orders list is empty
    for item in list_of_dict:
        order_id = item.get('AmazonOrderId')

        if order_id in orders_in_sold:
            print(f'{order_id} already in SOLD')
            continue

        # print(f'{order_id} NEW!')
        line_write.append(order_id)

        # Get order item details
        orders_items = orders_api.list_order_items(amazon_order_id=order_id)
        order_items_as_xml = orders_items.original
        with open('ListOrderItems.xml', 'w', encoding='utf-8') as f:
            f.write(order_items_as_xml)

        tree = ET.parse('ListOrderItems.xml')
        root = tree.getroot()

        str_to_cut = ''

        for each in root[0]:
            str_to_cut = reg_it(each.tag), ': ', each.text, ':'
            for sub_each in each:
                str_to_cut += '\n\t', reg_it(sub_each.tag), ': ', sub_each.text, ':'
                for ss_each in sub_each:
                    str_to_cut += '\n\t\t', reg_it(ss_each.tag), ': ', ss_each.text, ':'
                    for sss_each in ss_each:
                        str_to_cut += '\n\t\t\t', reg_it(sss_each.tag), ': ', sss_each.text, ':'

        # If zero items in the list, the 'join' will break
        str_to_cut = ''.join(str_to_cut)
        # print(str_to_cut)

        order_item_id = ';'.join(re.findall(r'OrderItemId: (\w+).*:', str_to_cut))
        line_write.append(order_item_id)

        purchase_date = item.get('PurchaseDate')
        line_write.append(purchase_date)

        payments_date = item.get('LastUpdateDate')
        line_write.append(payments_date)

        reporting_date = item.get('LastUpdateDate')
        line_write.append(reporting_date)

        promise_date = item.get('LatestShipDate')
        line_write.append(promise_date)

        days_past_promise = '0'
        line_write.append(days_past_promise)

        buyer_email = item.get('BuyerEmail')
        line_write.append(buyer_email)

        buyer_name = item.get('BuyerName')
        line_write.append(buyer_name)

        buyer_phone_number = item.get('Phone')
        line_write.append(buyer_phone_number)

        sku = ';'.join(re.findall(r'SellerSKU: (\w+-\w+-\w+).*:', str_to_cut))
        line_write.append(sku)

        product_name = ';'.join(re.findall(r'Title: (.+).*:', str_to_cut))
        line_write.append(product_name)

        quantity_purchased = ';'.join(re.findall(r'QuantityOrdered: (\d).*:', str_to_cut))
        line_write.append(quantity_purchased)

        quantity_shipped = ';'.join(re.findall(r'QuantityShipped: (\d).*:', str_to_cut))
        line_write.append(quantity_shipped)

        if ';' in quantity_purchased:
            quantity_to_ship_list = list()
            quantity_purchased_list = quantity_purchased.split(';')
            quantity_shipped_list = quantity_shipped.split(';')
            for i in range(len(quantity_purchased_list)):
                quantity_to_ship_list.append(str(int(quantity_purchased_list[i])-int(quantity_shipped_list[i])))
            quantity_to_ship = ';'.join(quantity_to_ship_list)
        else:
            quantity_to_ship = item.get('NumberOfItemsUnshipped')
        line_write.append(quantity_to_ship)

        ship_service_level = 'Standard'
        line_write.append(ship_service_level)

        recipient_name = item.get('Name')
        line_write.append(recipient_name)

        ship_address_1 = item.get('AddressLine1')
        line_write.append(ship_address_1)

        ship_address_2 = ''
        line_write.append(ship_address_2)

        ship_address_3 = ''
        line_write.append(ship_address_3)

        ship_city = item.get('City')
        line_write.append(ship_city)

        ship_state = item.get('StateOrRegion')
        line_write.append(ship_state)

        ship_postal_code = item.get('PostalCode')
        line_write.append(ship_postal_code)

        ship_country = item.get('CountryCode')
        line_write.append(ship_country)

        is_business_order = item.get('IsBusinessOrder')
        line_write.append(is_business_order)

        purchase_order_number = ''
        line_write.append(purchase_order_number)

        price_designation = ''
        line_write.append(price_designation)

        # IF YOU WANT TO ADD THE PRICE TO THE OUTPUT - UNCOMMENT
        # item_price = item.get('Amount')
        # line_write.append(item_price)
        #
        # item_tax = re.findall(r'ItemTax:\s+:\s+Amount: (\d+\.\d\d)', str_to_cut)[0]
        # line_write.append(item_tax)

        for i in range(len(line_write)):
            if line_write[i] is None:
                line_write[i] = ''

        line_w = '	'.join(line_write)
        print(line_w)
        line_w += '\n'
        with open(file_dir_name, 'a', encoding='utf-8') as f:
            f.write(line_w)

        line_write.clear()


    try:
        os.remove('ListOrders.xml')
        os.remove('ListOrderItems.xml')
    except Exception as ex:
        print(f'Could not delete .xml files: {ex}')


if __name__ == '__main__':
    source('.')
