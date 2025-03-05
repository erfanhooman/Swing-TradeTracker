from rest_framework.response import Response

def create_response(success: bool, status,
                    data = None, message: str = ''):
    """
    Create a JSON response with the given parameters.
    Args:
        success (bool): Indicates if the request was successful.
        status (int): HTTP status code (e.g., http_status.HTTP_400_BAD_REQUEST).
        data [dict]: Data to include in the response.
        message (str): Message to include in the response.
    Returns:
        HttpResponse: Response with the given parameters.
    """
    response = {
        'success': success,
        'message': message,
        'data': data,
    }
    return Response(response, status=status)
