# Ebay_ordering_assistant
This program was used to expedite ordering from Ebay (Dropshipping). In its core is Selenium automation, with AWS seller api calls. It downloads the Amazon seller orders, parses them, finds the items in Ebay by UPC barcode and lets you choose a seller. After that it semi automatically fills the customer address, chooses payment option and checkouts. Finally, it calculates profits and writes down the order. After execution it was uploading the data to a google sheet.
