response_message = {
    200: "Login successfully",
    201: "User registered successfully",
    202: "Logout successfully",
    203: "Data retrieved successfully",
    204: "Balance updated successfully",
    205: "Transaction created successfully",
    206: "Box closed successfully",
    207: "Transaction deleted successfully",

    400: "The value you provided is not valid",
    401: "Email Already registered",
    402: "Invalid refresh token",
    403: "Invalid Credentials",
    404: "Not found",
    407: "You cannot delete closed box transactions",

    500: "Unexpected error accord please try again later.."
}

serializer_response_message = {
    1: "At least two of 'price', 'amount', or 'value' must be provided",
    2: "Cannot be zero",
    3: "Invalid Value",
    4: "Insufficient USDT balance for this transaction",
    5: "Not enough coins to sell",
    6: "Invalid amount",
    7: "Amount must be a number",
    8: "Amount cannot be zero or negative value",
    9: "Coin not found",
    10: "There is no box for this coin",
    11: "You can't close this box, the total amount of the box must be zero",
    12: "There is no box with this id",
    13: "Invalid datetime format. Please use 'YYYY-MM-DD HH:MM:SS'. Example: '2024-02-04 15:30:00'."
}