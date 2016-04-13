import socket
import sys
#import urllib
import os
import mimetypes

def response_ok(body=b"this is a pretty minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->
        b'''
        HTTP/1.1 200 OK
        Content-Type: text/html
        <html><h1>Welcome:</h1></html>
        '''
    """
    # TODO: Update response_body so that it uses the provided body
    # and mimetype.
    resp = []
    resp.append(b"HTTP/1.1 200 OK")
    resp.append(b"Content-Type: {}".format(mimetype))
    resp.append(b"")
    resp.append(b"{}".format(body))
    return b"\r\n".join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp).encode('utf8')


def response_not_found():
    """returns a 404 Not Found response"""
    # TODO: Consruct and return a 404 response.
    #
    # See response_method_not_allowed for an example of
    # another type of 4xx response. You will need to use
    # the correct number (by changing "405") and also the
    # correct statement (by changing "Method Not Allowed").
    resp = []
    resp.append(b"HTTP/1.1 404 Not Found")
    resp.append(b"")
    # resp.append(b"You’ve asked for something that doesn’t exist")
    return b"\r\n".join(resp).encode('utf8')


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    return uri

def resolve_uri(uri):
    """This method should return appropriate content and a mime type"""    

    location = os.path.dirname(os.path.realpath(__file__)) + "/webroot" + uri

    if os.path.isdir(location):
        return "\r\n".join(os.listdir(location)).encode('utf8'), b"text/plain"

    elif os.path.isfile(location):
        with open(location, 'rb') as file:
            contents = file.read()
            file.close()

        return contents, mimetypes.MimeTypes().guess_type(location)[0].encode('utf8')

    else:
        raise NameError 

def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 35000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')
                    if len(data) < 1024:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    try:
                        content, mime_type = resolve_uri(uri)
                    except NameError:
                        response = response_not_found()
                    else:
                        response = response_ok(content, mime_type)

                print('sending response', file=log_buffer)
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)