from socket import *
import requests
import datetime
import threading

cache = {}

def handle_connection(client_socket, client_address):
    try:
        request_data = client_socket.recv(4096)
        print(f"Received request from {client_address}:\n{request_data.decode()}")
        response_data = handle_client_request(request_data)
        client_socket.sendall(response_data)
    except Exception as e:
        print(f"Error with {client_address}: {e}")
    finally:
        client_socket.close()

def run_proxy_server():
    proxy_host = '127.0.0.1'
    proxy_port = 8080

    proxy_socket = socket(AF_INET, SOCK_STREAM)
    proxy_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    proxy_socket.bind((proxy_host, proxy_port))

    proxy_socket.listen(5)
    print(f"Proxy Server listening on {proxy_host}:{proxy_port}")

    while True:
        client_socket, client_address = proxy_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Start a new thread for each connection
        # Using thread for multiple connection 
        client_thread = threading.Thread(target=handle_connection, args=(client_socket, client_address))
        client_thread.start()

def handle_client_request(request_data):
    try:
        first_line = request_data.splitlines()[0]
        method, url, _ = first_line.decode().split()

        # Handling GET method with web caching
        if method == 'GET':
            headers = {}
            if url in cache:
                _, last_modified = cache[url]
                headers['If-Modified-Since'] = last_modified
                print("Checking for updated content")

            response = requests.get(url, headers=headers)
            if response.status_code == 304:
                print("304 Not modified")
                content, _ = cache[url]
            else:
                print("200 OK")
                content = response.content
                last_modified = response.headers.get('Last-Modified', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'))
                cache[url] = (content, last_modified)

            return content

        # Handling POST method
        elif method == 'POST':
            # Extract headers and body for the POST request
            headers = { ... }  # Parse and add necessary headers
            body = request_data.split(b'\r\n\r\n')[1]
            response = requests.post(url, headers=headers, data=body)
        else:
            return b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    except Exception as e:
        print(f"Error handling request: {e}")
        return b"HTTP/1.1 500 Internal Server Error\r\n\r\n"

if __name__ == "__main__":
    run_proxy_server()
