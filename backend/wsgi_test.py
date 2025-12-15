import sys
import time

# Try to import FastAPI and measure time
try:
    start = time.time()
    from fastapi import FastAPI
    from a2wsgi import ASGIMiddleware
    import_time = time.time() - start
    import_status = f"Success ({import_time:.2f}s)"
except Exception as e:
    import_status = f"Failed: {e}"

def application(environ, start_response):
    status = '200 OK'
    output = f'Raw WSGI working! FastAPI Import: {import_status}'.encode('utf-8')
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
