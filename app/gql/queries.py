import strawberry
from typing import Optional
from gql.types import Project
from database.cosmos import container

@strawberry.type
class Query:
    @strawberry.field
    def projects(self, info) -> list[Project]:
        """Fetch all projects (auth required)."""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        results = list(container.read_all_items())
        
        # Convert results to a JSON-serializable list of dicts
        results_data = [
            {
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "createdAt": item["createdAt"],
                "updatedAt": item["updatedAt"]
            }
            for item in results
        ]

        # Return as Project objects
        return [Project(**item) for item in results_data]

    @strawberry.field
    def get_project(self, info, project_id: str) -> Optional[Project]:
        """Fetch a single project by ID (auth required)."""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        try:
            item = container.read_item(item=project_id, partition_key=project_id)
            project_data = {
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "createdAt": item["createdAt"],
                "updatedAt": item["updatedAt"]
            }

            return Project(**project_data)
        except Exception:
            return None

    @strawberry.field
    def hello(self) -> str:
        """Public endpoint - no auth required"""
        message = "Hello World! This endpoint doesn't require authentication."
        return message

    @strawberry.field
    def whoami(self, info) -> str:
        """Check current authentication status"""
        user = info.context.get("user")
        if user:
            result = f"Authenticated as: {user.get('preferred_username', 'Unknown user')}"
        else:
            result = "Not authenticated"
        return result