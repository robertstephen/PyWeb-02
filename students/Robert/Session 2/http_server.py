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
    resp.append(b"Content-Type: " + mimetype)
    resp.append(b"")
    resp.append(body)
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
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    # resp.append("You’ve asked for something that doesn’t exist")
    return "\r\n".join(resp).encode('utf8')


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    return uri

def resolve_uri(uri):
    """
    This method should return appropriate content and a mime type.
    If the requested URI is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.
    If the URI is a file, it should return the contents of that file
    and its correct mimetype.
    If the URI does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.
    Ex:
        resolve_uri('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")
        )
        resolve_uri('/sample_1.png') -> (b"A12BCF...",  # contents of sample_1.png
                                         b"image/png")
        )
        resolve_uri('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")
        resolve_uri('/a_page_that_doesnt_exist.html') -> Raises a NameError
    """
    content = ""
    mime_type = ""
    # get the path
    link = os.path.dirname(os.path.realpath(__file__)) + "/webroot" + uri
    # try open the link
    try:
    # try if it's a file
        if os.path.isfile(link) == False:
            content = ",".join(os.listdir(link)).encode('utf8') 
            mime_type = b"text/plain"
        else:
    # open file if it's a file
            with open(link, 'rb') as f:
                content = f.read()
                f.close()
    # raise special case of python files
            if uri.endswith(".py"):
                mime_type = b"text/x-python"
            else:
                mime_type = mimetypes.guess_type(link)[0].encode('utf8')
    # raise name error if can't open the link
    except IOError:
        raise NameError
    # return the values of content and mime_type
    return content, mime_type


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