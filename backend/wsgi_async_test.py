import sys
import asyncio
import nest_asyncio

# Apply patch immediately
nest_asyncio.apply()

def application(environ, start_response):
    output_lines = []
    
    # 1. Test basic python
    output_lines.append(b"1. Python is running")
    
    # 2. Test Asyncio
    try:
        async def async_hello():
            await asyncio.sleep(0.1)
            return b"2. Asyncio is working!"
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_hello())
        output_lines.append(result)
        loop.close()
    except Exception as e:
        output_lines.append(f"2. Asyncio FAILED: {e}".encode('utf-8'))

    # Return response
    status = '200 OK'
    output = b'\n'.join(output_lines)
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
