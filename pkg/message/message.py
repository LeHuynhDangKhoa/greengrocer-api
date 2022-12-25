class Constants:
    pass

counter = 1
for constant in ['MSG_INVALID_CATEGORY_ID', 'MSG_INVALID_STAR', 'MSG_INVALID_DISCOUNT', 'MSG_INVALID_PRICE_FROM',
                'MSG_INVALID_PRICE_TO', 'MSG_INVALID_ORDER', 'MSG_INVALID_LIMIT', 'MSG_INVALID_OFFSET',
                'MSG_INVALID_PRODUCT_ID', 'MSG_PRODUCT_NOT_FOUND']:
    setattr(Constants, constant, counter)
    counter += 1

Message = {
    Constants.MSG_INVALID_CATEGORY_ID: "category_id parameter must be a positive number",
    Constants.MSG_INVALID_STAR: "star parameter must be a positive number",
    Constants.MSG_INVALID_DISCOUNT: "discount parameter must be true or false",
    Constants.MSG_INVALID_PRICE_FROM: "price_from parameter must be greater than or equal to 0",
    Constants.MSG_INVALID_PRICE_TO: "price_to parameter must be greater than or equal to 0",
    Constants.MSG_INVALID_ORDER: "order parameter must be asc or desc",
    Constants.MSG_INVALID_LIMIT: "limit parameter must be a positive number",
    Constants.MSG_INVALID_OFFSET: "offset parameter must be greater than or equal to 0",
    Constants.MSG_INVALID_PRODUCT_ID: "product id parameter must be a number",
    Constants.MSG_PRODUCT_NOT_FOUND: "This product had been deleted or does not exist",
}



