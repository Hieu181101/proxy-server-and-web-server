from socket import *
import os
import re
from datetime import datetime


def handle_http_requests(request):
    method, path, http_version = request.split(' ', 2)

    if method == 'GET':
        # If the user is requesting an unauthorized file return True, else return False.
        if not check_credentials(path):
            return "HTTP/1.1 403 Forbidden\r\n\r\n403 Forbidden"
        else:
            return handle_get_request(path, request)

    elif method == 'POST':
        if not validateContentLength(request):
            return "HTTP/1.1 411 Length Required\r\n\r\n411 Length Required"

    else:
        return "HTTP/1.1 400 Bad Request\r\n\r\n400 Bad Request"


def check_credentials(path):
    if path == "/unauthorized.html":
        return False
    else:
        return True


def handle_get_request(path, request):
    # Holds the absolute path of the main.py (same as the absolute path of the requested file).
    base_directory = os.path.abspath(os.path.dirname(__file__))

    # Adding the requested file path (without the initial /) to the absolute path.
    file_path = os.path.join(base_directory, path[1:])

    # Checking if the file exists in the current directory.
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Before sending the content of the requested page we check if the HTTP request has an If-Modified-Since
        # field in the header. If yes, we'll compare the last modification date with the date in the field. If the
        # condition is True, server continues sending the content, if False, the server sends an 304 Not Modified
        # status code.
        if check_if_modified_since(file_path, request):
            return "HTTP/1.1 304 Not Modified\r\n\r\n304 Not Modified"

        else:
            with open(file_path, 'r') as file:
                content = file.read()

            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{content}"
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"

    return response


def check_if_modified_since(file_path, request):
    last_modification_time = os.path.getmtime(file_path)  # Unix timestamp
    last_modification_datetime = datetime.utcfromtimestamp(last_modification_time)

    if 'If-Modified-Since' in request:
        HTTP_request_modification_date = request.split('If-Modified-Since: ')[1].split('\r\n')[0]

        # Convert date string to datetime object
        HTTP_request_datetime = datetime.strptime(HTTP_request_modification_date, '%a, %d %b %Y %H:%M:%S GMT')

        if last_modification_datetime > HTTP_request_datetime:
            return True
        else:
            return False
    else:
        return False


# This function returns True if the provided HTTP request contains Content-Length field and False otherwise.
def validateContentLength(request):
    pattern = r"Content-Length:\s*(\d+)"

    match = re.search(pattern, request)
    if match:
        return True
    else:
        return False


def run_web_server():
    server_host = '127.0.0.1'
    server_port = 8080

    # Creating a socket for the web server
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((server_host, server_port))

    # Listening for the incoming connections
    server_socket.listen(1)
    print(f"Server listening on {server_host}:{server_port}")

    while True:
        # Accepting a connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Receiving data from the client.
        requested_data = client_socket.recv(1024).decode('utf-8')
        print(f"Received data:\n"
              f"{requested_data}")

        # Handling the request and generating a response
        response_data = handle_http_requests(requested_data)

        # Send the response back to the client
        client_socket.sendall(response_data.encode('utf-8'))

        # Close the connection
        client_socket.close()
        print("Connection closed\n")


if __name__ == "__main__":
    run_web_server()




