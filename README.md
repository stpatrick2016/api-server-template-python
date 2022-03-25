# Basic API Server on Python with authentication
Templates for barebone API server in Python, which can be copied and used as a starting point of any API project

#### Supported features:
* [Authentication](#authentication)
  * Plain credentials
  * Google
  * Refresh token
* Protecting Flask views
* [Logging](#logging)
  * Application insights



## Authentication
Supported modes: plain credentials and Google authentication. To protect Flask's views, use `authorize` decorator. Authentication methods are additive (can use any combination of them)

#### Plain credentials
Search and implement `validate_user` function

#### Google authentication
Supply `GOOGLE_CLIENT_ID` as environment variable

## Logging
Simply import logger at the top of the .py file and use as usual [Python logger](https://docs.python.org/3/library/logging.html):
```python
from common import get_logger

logger = get_logger(__name__)
```

To log into Microsoft's [Application Insights](https://azure.microsoft.com/en-us/services/monitor/):
1. Uncomment `opencensus-ext-azure==1.1.0` in the requirements.txt file
2. Supply the connection string as `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
