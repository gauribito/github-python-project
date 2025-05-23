"""
Integration Utilities Module

This module provides utilities for managing and monitoring Bito integrations,
particularly focusing on repository status management and monitoring.

It contains helper functions for waiting on repository status changes,
which is useful for integration testing and automation workflows.

Features:
- Asynchronous polling for repository status changes
- Configurable timeout and polling intervals
- Detailed logging of status changes
- Error handling for common integration issues

Dependencies:
- asyncio
- time
- utils.logger

Usage Example:
    ```python
    # Create an instance with a BitoAPI object
    integration_utils = IntegrationUtils(bito_api)
    
    # Wait for a repository to reach PAUSED status
    try:
        repo = await integration_utils.wait_for_repo_status_paused(
            workspace_id=123,
            integration_id=456,
            repository_name="org/repo"
        )
        print(f"Repository paused successfully: {repo}")
    except TimeoutError as e:
        print(f"Timed out waiting for repository status: {e}")
    ```
"""

import asyncio
import time
from typing import Any, Dict
from utils.logger import get_logger

class IntegrationUtils:
    """
    Utility class for managing and monitoring Bito integrations.
    
    This class provides helper methods for common integration operations,
    such as waiting for specific repository statuses and monitoring integration
    configuration changes.
    
    Attributes:
        bito_api: An instance of BitoAPI using Playwright APIRequestContext
        logger: Logger instance for this class
    """
    
    def __init__(self, bito_api):
        """
        Initialize the IntegrationUtils class.
        
        Args:
            bito_api: An instance of BitoAPI that provides methods for interacting
                     with the Bito API. Expected to be using Playwright's
                     APIRequestContext under the hood.
        """
        self.bito_api = bito_api  # Expected to be an instance of BitoAPI using Playwright APIRequestContext
        self.logger = get_logger("IntegrationUtils")

    async def wait_for_repo_status_paused(
        self,
        workspace_id: int,
        integration_id: int,
        repository_name: str,
        timeout_ms: int = 15000,
        interval_ms: int = 1000
    ) -> Dict[str, Any]:
        """
        Waits until a specific repository under an integration becomes 'PAUSED'.
        
        This method polls the API at regular intervals until the specified repository
        reaches the 'PAUSED' status or until the timeout is reached.
        
        Args:
            workspace_id (int): The ID of the workspace containing the integration
            integration_id (int): The ID of the integration containing the repository
            repository_name (str): The full name of the repository (e.g., 'org/project')
            timeout_ms (int, optional): Maximum time to wait in milliseconds. Defaults to 15000.
            interval_ms (int, optional): Interval between status checks in milliseconds. Defaults to 1000.

        Raises:
            ValueError: If the integration configuration is invalid or the repository is not found
            TimeoutError: If the repository status does not become PAUSED within the timeout period

        Returns:
            Dict[str, Any]: The repository configuration item with status 'PAUSED'
        """
        start_time = time.time()
        self.logger.info(f"Waiting for repository '{repository_name}' to become PAUSED (timeout: {timeout_ms/1000}s)")

        while (time.time() - start_time) * 1000 < timeout_ms:
            self.logger.debug(f"Checking repository status for '{repository_name}'")
            response = await self.bito_api.get_all_agent_configuration(workspace_id, integration_id)
            config_list = response.get("configuration", [])

            config = next((c for c in config_list if c.get("integrationId") == integration_id), None)

            if not config or not isinstance(config.get("items"), list):
                raise ValueError("❌ Invalid integration configuration or missing items list")

            matching_item = next((item for item in config["items"] if item.get("name") == repository_name), None)

            if not matching_item:
                raise ValueError(f"❌ Repository '{repository_name}' not found in integration items.")

            self.logger.debug(f"Checking repo status... Current: {matching_item['status']}")

            if matching_item["status"] == "PAUSED":
                self.logger.info(f"Repository '{repository_name}' is now PAUSED")
                return matching_item

            await asyncio.sleep(interval_ms / 1000)

        raise TimeoutError(f"⏱️ Timeout: Repo '{repository_name}' status did not become 'PAUSED' within {timeout_ms // 1000}s")
