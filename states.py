# State definitions for user order
SHOPS, MENU, RECORD = range(0, 3)
# State definitions for second level user management
USER_ACTION, INPUT_USERNAME, INPUT_ROLE, userCONFIRMATION = range(3, 7)

# State definition for second level transaction management
TRANSACTION_ACTION, TRANSACTION_AMOUNT, TRANSACTION_PAYEE, TRANSACTION_ITEM, TRANSACTION_CONFIRMATION, TRANSACTION_OUTCOME = range(
    7, 13)


# Meta states
MAIN, MAIN_SELECT = map(
    chr, range(13, 15))

# State definitions for second level inventory management
SHOP_ACTION, GET_CREDITS, ADD_ITEM = range(15, 18)
