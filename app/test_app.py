import os
import uuid
import pytest
import httpx
from dotenv import load_dotenv
load_dotenv()  # loads .env variables automatically

BASE_URL = "http://localhost:8000/graphql"
TOKEN = os.getenv("AZURE_AD_ACCESS_TOKEN")  # Azure AD token for authenticated tests
HEADERS_AUTH = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
HEADERS_NOAUTH = {}

# --- Helper functions ---
def gql_query(query: str, headers=None):
    headers = headers or {}
    response = httpx.post(BASE_URL, json={"query": query}, headers=headers)
    return response

# --- Public endpoint tests ---
def test_hello():
    response = gql_query("{ hello }", headers=HEADERS_NOAUTH)
    assert response.status_code == 200
    assert response.json()["data"]["hello"].startswith("Hello World")

def test_whoami_noauth():
    response = gql_query("{ whoami }", headers=HEADERS_NOAUTH)
    assert response.status_code == 200
    assert response.json()["data"]["whoami"] == "Not authenticated"

# --- Authenticated query tests ---
@pytest.mark.skipif(not TOKEN, reason="AZURE_AD_ACCESS_TOKEN not set")
def test_whoami_auth():
    response = gql_query("{ whoami }", headers=HEADERS_AUTH)
    assert response.status_code == 200
    assert "Authenticated as" in response.json()["data"]["whoami"]

@pytest.mark.skipif(not TOKEN, reason="AZURE_AD_ACCESS_TOKEN not set")
def test_projects_query():
    response = gql_query("{ projects { id name description } }", headers=HEADERS_AUTH)
    assert response.status_code == 200
    # Can be empty list if no projects exist
    assert "data" in response.json()
    assert "projects" in response.json()["data"]

# --- Mutation tests ---
@pytest.mark.skipif(not TOKEN, reason="AZURE_AD_ACCESS_TOKEN not set")
def test_create_update_delete_project():
    # 1. Create project
    project_name = "Test Project " + str(uuid.uuid4())
    project_desc = "Test Description"
    mutation_create = f'''
    mutation {{
        createProject(name: "{project_name}", description: "{project_desc}") {{
            id
            name
            description
        }}
    }}
    '''
    response = gql_query(mutation_create, headers=HEADERS_AUTH)
    assert response.status_code == 200
    data = response.json()["data"]["createProject"]
    project_id = data["id"]
    assert data["name"] == project_name
    assert data["description"] == project_desc

    # 2. Update project
    updated_name = project_name + " Updated"
    mutation_update = f'''
    mutation {{
        updateProject(projectId: "{project_id}", name: "{updated_name}") {{
            id
            name
            description
        }}
    }}
    '''
    response = gql_query(mutation_update, headers=HEADERS_AUTH)
    assert response.status_code == 200
    data = response.json()["data"]["updateProject"]
    assert data["name"] == updated_name

    # 3. Delete project
    mutation_delete = f'''
    mutation {{
        deleteProject(projectId: "{project_id}")
    }}
    '''
    response = gql_query(mutation_delete, headers=HEADERS_AUTH)
    assert response.status_code == 200
    assert response.json()["data"]["deleteProject"] is True

    # 4. Confirm deletion
    query_get = f'''
    query {{
        getProject(projectId: "{project_id}") {{
            id
            name
        }}
    }}
    '''
    response = gql_query(query_get, headers=HEADERS_AUTH)
    assert response.status_code == 200
    assert response.json()["data"]["getProject"] is None

# --- Error handling tests ---
def test_projects_noauth_error():
    response = gql_query("{ projects { id name } }", headers=HEADERS_NOAUTH)
    # Should return error inside "errors"
    assert response.status_code == 200
    assert "errors" in response.json()
    assert response.json()["errors"][0]["message"] == "Authentication required"
