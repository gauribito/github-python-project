"""
API Utilities Module for HTTP Request Handling

This module provides a wrapper around Playwright's API request functionality
to simplify making HTTP requests in an asynchronous context. It handles
common tasks such as request building, response parsing, and resource management.

The ApiUtils class implements the async context manager protocol for proper
resource initialization and cleanup, and provides methods for all common
HTTP methods (GET, POST, PUT, DELETE).

Features:
- Async context manager support for proper resource lifecycle management
- Consistent error handling and logging
- Automatic header management
- JSON response parsing
- Configurable base URL and default headers

Usage Example:
    ```python
    async with ApiUtils.initialize_new_instance("https://api.example.com") as api:
        response = await api.get("users/123")
        user_data = await api.parse_response(response)
        print(user_data)
    ```

Dependencies:
- playwright.async_api
- asyncio
- json
- utils.logger
"""

from playwright.async_api import async_playwright, APIResponse
from typing import Dict, Optional, Union, Any
import json
import asyncio
from utils.logger import get_logger

class ApiUtils:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize API utilities with base URL and headers.
        
        Args:
            base_url (str): The base URL for all API requests
            headers (Optional[Dict[str, str]]): Default headers to include with all requests
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.playwright = None
        self.context = None
        self._initialized = False
        self.logger = get_logger("ApiUtils")

    @classmethod
    async def initialize_new_instance(cls, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Factory method to create and fully initialize a new ApiUtils instance.
        
        This is a convenience method that creates a new instance and calls init() on it.
        
        Args:
            base_url (str): The base URL for all API requests
            headers (Optional[Dict[str, str]]): Default headers to include with all requests
            
        Returns:
            ApiUtils: A fully initialized ApiUtils instance
            
        Raises:
            RuntimeError: If initialization fails
        """
        api = cls(base_url, headers)
        await api.init()
        return api

    async def init(self):
        """
        Initialize the Playwright API context.
        
        This method starts the Playwright process and creates a new request context
        with the configured base URL and headers.
        
        Raises:
            RuntimeError: If initialization fails
        """
        if self._initialized:
            return  # Already initialized
            
        try:
            self.playwright = await async_playwright().start()
            self.context = await self.playwright.request.new_context(
                base_url=self.base_url,
                extra_http_headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    **self.headers,
                }
            )
            self._initialized = True
        except Exception as e:
            # Clean up resources if initialization fails
            await self.cleanup_resources()
            raise RuntimeError(f"Failed to initialize API context: {str(e)}") from e

    async def cleanup_resources(self):
        """
        Close and clean up Playwright resources.
        
        This method disposes of the request context and stops the Playwright
        process, releasing all associated resources.
        """
        if self.context:
            await self.context.dispose()
            self.context = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            
        self._initialized = False

    # Special methods for async context manager support with better names
    async def start_session(self):
        """
        Start an API session and initialize resources.
        
        This method is an alias for init() and is used when the class is used
        as an async context manager.
        
        Returns:
            self: The ApiUtils instance for method chaining
        """
        await self.init()
        return self

    async def end_session(self, exc_type=None, exc_val=None, exc_tb=None):
        """
        End an API session and clean up resources.
        
        This method is an alias for cleanup_resources() and is used when the
        class is used as an async context manager.
        
        Args:
            exc_type: Exception type if an exception was raised in the context
            exc_val: Exception value if an exception was raised in the context
            exc_tb: Exception traceback if an exception was raised in the context
        """
        await self.cleanup_resources()
        
    # Aliases for Python's context manager protocol
    __aenter__ = start_session
    __aexit__ = end_session

    def _ensure_initialized(self):
        """
        Ensure the API context is initialized.
        
        Raises:
            RuntimeError: If the API context is not initialized
        """
        if not self._initialized or not self.context:
            raise RuntimeError("API context not initialized. Call init() method first or use with start_session()/end_session().")

    def _format_url(self, endpoint: str) -> str:
        """
        Format the full URL for logging purposes.
        
        Args:
            endpoint (str): The API endpoint path
            
        Returns:
            str: The full URL (base URL + endpoint)
        """
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    async def get(
            self,
            endpoint: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Union[str, int]]] = None
    ) -> APIResponse:
        """
        Perform a GET request.
        
        Args:
            endpoint (str): API endpoint to request
            headers (Optional[Dict[str, str]]): Additional headers for this request
            params (Optional[Dict[str, Union[str, int]]]): Query parameters
            
        Returns:
            APIResponse: Playwright API response object
            
        Raises:
            RuntimeError: If the API context is not initialized
        """
        self._ensure_initialized()
        
        full_url = self._format_url(endpoint)
        self.logger.info(f"[GET] Hitting URL: {full_url}")
        self.logger.debug(f"Params: {params}")
        self.logger.debug(f"Headers: {headers}")

        return await self.context.get(
            endpoint,
            headers={**self.headers, **(headers or {})},
            params=params or {}
        )

    async def post(
            self,
            endpoint: str,
            data: Optional[Dict] = None,
            headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Perform a POST request with JSON data.
        
        Args:
            endpoint (str): API endpoint to request
            data (Optional[Dict]): JSON data to send in the request body
            headers (Optional[Dict[str, str]]): Additional headers for this request
            
        Returns:
            APIResponse: Playwright API response object
            
        Raises:
            RuntimeError: If the API context is not initialized
        """
        self._ensure_initialized()
        
        full_url = self._format_url(endpoint)
        self.logger.info(f"[POST] Hitting URL: {full_url}")
        self.logger.debug(f"Headers: {headers}")
        self.logger.debug(f"JSON: {json.dumps(data, indent=2) if data else None}")

        return await self.context.post(
            endpoint,
            headers={**self.headers, **(headers or {})},
            data=data
        )

    async def put(
            self,
            endpoint: str,
            data: Optional[Dict] = None,
            headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Perform a PUT request with JSON data.
        
        Args:
            endpoint (str): API endpoint to request
            data (Optional[Dict]): JSON data to send in the request body
            headers (Optional[Dict[str, str]]): Additional headers for this request
            
        Returns:
            APIResponse: Playwright API response object
            
        Raises:
            RuntimeError: If the API context is not initialized
        """
        self._ensure_initialized()
        
        full_url = self._format_url(endpoint)
        self.logger.info(f"[PUT] Hitting URL: {full_url}")
        self.logger.debug(f"Headers: {headers}")
        self.logger.debug(f"JSON: {json.dumps(data, indent=2) if data else None}")

        return await self.context.put(
            endpoint,
            headers={**self.headers, **(headers or {})},
            data=data
        )

    async def delete(
            self,
            endpoint: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Union[str, int]]] = None
    ) -> APIResponse:
        """
        Perform a DELETE request.
        
        Args:
            endpoint (str): API endpoint to request
            headers (Optional[Dict[str, str]]): Additional headers for this request
            params (Optional[Dict[str, Union[str, int]]]): Query parameters
            
        Returns:
            APIResponse: Playwright API response object
            
        Raises:
            RuntimeError: If the API context is not initialized
        """
        self._ensure_initialized()
        
        full_url = self._format_url(endpoint)
        self.logger.info(f"[DELETE] Hitting URL: {full_url}")
        self.logger.debug(f"Params: {params}")
        self.logger.debug(f"Headers: {headers}")

        return await self.context.delete(
            endpoint,
            headers={**self.headers, **(headers or {})},
            params=params or {}
        )

    async def parse_response(self, response: APIResponse) -> Any:
        """
        Parse an API response based on its content type.
        
        This method handles different response types based on the content-type header.
        For JSON responses, it parses the response body as JSON. For other types,
        it returns the response text.
        
        Args:
            response (APIResponse): The API response to parse
            
        Returns:
            Any: Parsed response data (JSON object or string)
            
        Raises:
            ValueError: If the response has an error status code (4xx/5xx)
        """
        if not response:
            self.logger.warning("Received invalid response object")
            return None

        try:
            # Check status code first
            if hasattr(response, "status") and response.status >= 400:
                error_text = await response.text() if hasattr(response, "text") else "No error details available"
                raise ValueError(f"HTTP Error {response.status}: {error_text}")

            # Check if headers attribute exists and is accessible
            content_type = response.headers.get("content-type", "") if hasattr(response, "headers") else ""

            if "application/json" in content_type:
                return await response.json()
            return await response.text()
        except (ValueError, AttributeError, json.JSONDecodeError) as e:
            self.logger.exception("Error parsing response: %s", e)
            # Return the raw response or None depending on your error handling strategy
            return None
