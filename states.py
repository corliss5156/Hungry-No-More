# State definitions for ???
SHOPS, MENU, RECORD = range(0, 3)
# State definitions for second level user management
USER_ACTION, INPUT_USERNAME, INPUT_ROLE, userCONFIRMATION = range(3, 7)

# State definition for second level transaction management
TRANSACTION_ACTION, TRANSACTION_AMOUNT, TRANSACTION_PAYEE, TRANSACTION_ITEM, TRANSACTION_CONFIRMATION = range(
    7, 12)

# State definition for second level fund management
FUND_ACTION, FUND_AMOUNT, FUND_MANAGER, FUND_CONFIRMATION = range(
    12, 16)

# # Meta states
MAIN_SELECT = map(chr, range(16, 17))
