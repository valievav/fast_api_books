import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def register_middleware(app: FastAPI):

    @app.middleware('http')
    async def custom_logging(request: Request, call_next):
        """
        Provide custom logging
        """
        start_time = time.time()

        response = await call_next(request)

        processed_time = time.time() - start_time
        message = f'{request.method} - {request.url.path} - {response.status_code} - completed in {processed_time} s'
        print(message)

        return response

    # commenting, since it blocks new user from signing up (they have no auth yet)
    # @app.middleware('http')
    # async def authorization(request: Request, call_next):
    #     """
    #     Check if 'Authorization' is passed in request headers for API calls
    #     """
    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #             content={'message': 'Not Authenticated',
    #                      'resolution': 'Please provide valid credentials'},
    #             status_code=status.HTTP_401_UNAUTHORIZED
    #         )
    #     response = await call_next(request)
    #     return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_headers=['*'],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=['localhost', '127.0.0.1']
    )
