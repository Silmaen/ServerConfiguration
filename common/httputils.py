"""
Module gathering http operations
"""
import base64
import http.client
import urllib.parse
from common.maintenance import logger


def get_http_response(url: str, user: str = "", password: str = ""):
    """
    do http requests
    :param url: the url to get the response
    :param user: user to use for request if needed
    :param password: password associated to the user
    :return: the http result
    """
    valid_type = ["http", "https"]
    if "://" not in url:
        url = "http://" + url
    dec = urllib.parse.urlparse(url)
    if "." not in dec.netloc:
        logger.log_error("get_http_response", "Bad hostname: " + dec.netloc)
        return False, None
    if dec.scheme not in valid_type:
        logger.log_error("get_http_response", "unsupported dec.scheme: '" + dec.scheme + "' valid type: " + str(valid_type))
        return False, None
    try:
        # connection
        if dec.scheme == "http":
            h2 = http.client.HTTPConnection(dec.netloc, timeout=50)
        elif dec.scheme == "https":
            h2 = http.client.HTTPSConnection(dec.netloc, timeout=50)
        request = dec.path
        # request construction
        if dec.query != "":
            request += "?" + dec.query
        h2.putrequest("GET", request)
        # adding user information
        if user != "":
            auth_str = user + ":" + password
            auth_string = base64.b64encode(auth_str.encode("ascii")).decode("ascii").replace('\n', '')
            h2.putheader("AUTHORIZATION", "Basic " + auth_string)
        h2.endheaders()
        return True, h2
    except TimeoutError as err:
        logger.log_error("get_http_response", "Error: Request to: " + str(dec.netloc) + " has timed out!!")
        return False, None
    except http.client.HTTPException as err:
        logger.log_error("get_http_response", "Error: Request to: " + str(dec.netloc) + " has http error: " + str(err))
        return False, None
    except Exception as err:
        logger.log_error("get_http_response", "Error: Request to: " + str(dec.netloc) + " has unknown error: " + str(err))
        return False, None


def exist_http_page(url: str, user: str = "", password: str = ""):
    """
    test if an http page exists
    :param url: the url to test
    :param user: eventually the user for connection
    :param password: the password associated with the user
    :return: True if the page exist and is accessible
    """
    res, h2 = get_http_response(url, user, password)
    rep = False
    if res:
        rep = h2.getresponse().status == 200
        h2.close()
    return rep


def get_http_page(url: str, user: str = "", password: str = ""):
    """
    get the content of the http page
    :param url: the url to get
    :param user: eventually the user for connection
    :param password: the password associated with the user
    :return: the content of the page
    """
    res, h2 = get_http_response(url, user, password)
    http_response = h2.getresponse()
    if not res:
        logger.log_error("getHttpPage", " problem code: ")
        return []
    try:
        http_data = http_response.read().decode("ascii").splitlines()
    except Exception as err:
        logger.log_error("getHttpPage", " problem during response dedoding: " + str(err))
        http_data = []
    if http_response.status != 200:
        logger.log_error("getHttpPage", "ERROR " + str(http_response.status) + " : " + str(http_response.reason))
    h2.close()
    return http_data

