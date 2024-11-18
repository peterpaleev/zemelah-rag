from butter_cms import ButterCMS
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)

client = ButterCMS('bfaeec8f74834094df713acaaeed45d547d884b9')

try:
    sample_page = client.pages.get('*', 'shikheev-vladimir')
    # Pretty print the response
    print('Response data:')
    print(json.dumps(sample_page['data'], indent=2))
except Exception as e:
    print(f'Error occurred: {str(e)}')
    # If there's a response object in the error, print it
    if hasattr(e, 'response'):
        print(f'Response status: {e.response}')
        print('Response body:')
