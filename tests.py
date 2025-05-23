"""
Bito API Integration Test Module

This module contains tests for the Bito API integration functionality,
specifically focusing on integration creation, repository discovery, and
repository enablement workflows.

The test creates a GitLab Enterprise integration, waits for a specific repository
to be discovered and paused, then enables that repository for use with Bito.

Functions:
    test_bito_api_integration: Main test function for Bito API integration flow

Dependencies:
    - BitoAPI: Client for interacting with Bito API endpoints
    - IntegrationUtils: Utility for waiting on integration state changes
    - Environment variables: GITLAB_ACCESS_TOKEN, BITO_API_BASE_URL, BITO_API_KEY

Example:
    Run this test with:
    ```
    python -m asyncio tests/api/test_bito_api.py
    ```
"""

import asyncio
import random
from env import get_env
from utils.integration_utils import IntegrationUtils
from api.bito_api import BitoAPI, CreateIntegrationData, UpdateIntegrationData
from utils.logger import get_logger

logger = get_logger("Bito API Test")

async def test_bito_api_integration():
    """
    Test the Bito API integration workflow.
    
    This test performs the following steps:
    1. Initialize the Bito API client
    2. Get existing integration details for the workspace
    3. Create a new GitLab Enterprise integration
    4. Wait for a specific repository to be discovered and paused
    5. Enable the repository for use with Bito
    """
    logger.info("Starting Bito Integration API Test...")

    # Environment setup
    gitlab_access_token = get_env("GITLAB_ACCESS_TOKEN")
    repository_name = "gauri.desai.ent.12/gauri-egitlab-go-project"

    # Initialize BitoAPI (handles request context setup)
    bito_api = await BitoAPI.init()

    # Input details
    workspace_id = 25252
    user_id = 25115
    integration_type = "GIT"
    integration_subtype = "gitlab-enterprise"
    organisation_name = "Gauri Desai"
    organisation_id=str(random.randint(10, 99))
    account_type = "PERSONAL"
    user_access = "Owner"
    integration_domain = "https://gitlab.bito.ai/"
    create_integration_status = "CONFIG_PENDING"

    # Get integration details for the workspace
    print(f"🔍 Getting integration details for workspace ID: {workspace_id}")
    integration_details_list = await bito_api.get_integration_details(workspace_id)
    print(f"✅ Retrieved integration details: {integration_details_list}")
    get_integration_detail = next((item for item in integration_details_list if item is not None), {}) if integration_details_list else {}

    # # Cleanup before integration creation - Delete existing integration
    # delete_data = UpdateIntegrationData(
    #     id=get_integration_detail.get("id"),
    #     workspaceId=workspace_id,
    #     userId=get_integration_detail.get("userId"),
    #     email=get_integration_detail.get("email"),
    #     integrationType=get_integration_detail.get("integrationType", ""),
    #     integrationSubType=get_integration_detail.get("integrationSubType", ""),
    #     integrationDetails=get_integration_detail.get("integrationDetails", {}),
    #     organisationName=get_integration_detail.get("organisationName", ""),
    #     organisationId=get_integration_detail.get("organisationId", ""),
    #     defaultConfigId=get_integration_detail.get("defaultConfigId", ""),
    #     accountType=get_integration_detail.get("accountType", ""),
    #     userAccess=get_integration_detail.get("userAccess", ""),
    #     integrationDomain=get_integration_detail.get("integrationDomain", ""),
    #     status='UNINSTALLED'
    # )

    # # Step 3: Call delete_integration with the created data
    # print(f"Deleting integration for workspace ID: {workspace_id}")
    # result = await bito_api.update_integration(delete_data)
    # print(f"Integration deleted successfully: {result}")

    # Create integration payload
    integration_data = CreateIntegrationData(
        workspaceId = workspace_id,
        userId = user_id,
        integrationType = integration_type,
        integrationSubType = integration_subtype,
        integrationDetails = {
            "git-token-text": gitlab_access_token,
            "token-type": "personal_access_token"
        },
        organisationName = organisation_name,
        organisationId = organisation_id,
        accountType = account_type,
        userAccess = user_access,
        integrationDomain = integration_domain,
        status = create_integration_status
    )

    # Create the integration
    integration = await bito_api.create_integration(integration_data)
    assert "id" in integration, "Integration creation failed: No ID"
    assert "organisationId" in integration, "Integration response missing organisationId"
    assert integration["status"] == "CONFIG_PENDING", f"Unexpected status: {integration['status']}"

    integration_id = integration["id"]
    workspace_id = integration_data.workspaceId
    organisation_id = integration["organisationId"]
    logger.info("Integration created successfully")
    logger.info(f"Integration ID: {integration_id}")
    logger.info(f"Workspace ID: {workspace_id}")
    logger.info(f"Organisation ID: {organisation_id}")

    # ⏳ Wait for repo status to become PAUSED
    integration_utils = IntegrationUtils(bito_api)
    repo = await integration_utils.wait_for_repo_status_paused(workspace_id, integration_id, repository_name)

    repo_id = repo["id"]
    logger.info(f"Repository ID: {repo_id}")
    logger.info(f"Repository Status: {repo['status']}")

    # Enable repository
    enable_response = await bito_api.enable_repository(integration_id, workspace_id, repo_id)

    assert isinstance(enable_response, list), "❌ Enable repo response is not a list"
    matching_repo = next((item for item in enable_response if item.get("id") == repo_id), None)

    assert matching_repo is not None, "Repository not found in response"
    assert "status" in matching_repo, "Missing status in repo response"
    assert matching_repo["status"] == "SUCCESS", f"Unexpected repo status: {matching_repo['status']}"

    logger.info("Repository enabled successfully")
