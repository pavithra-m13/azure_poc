import strawberry
import uuid
from datetime import datetime
from typing import Optional
from gql.types import Project
from database.cosmos import container

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_project(self, info, name: str, description: str) -> Project:
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        now = datetime.utcnow().isoformat()
        project_id = str(uuid.uuid4())
        new_item = {
            "id": project_id,
            "name": name,
            "description": description,
            "createdAt": now,
            "updatedAt": now,
        }
        container.create_item(new_item)
        return Project(**new_item)

    @strawberry.mutation
    def update_project(self, info, project_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Project]:
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        try:
            item = container.read_item(item=project_id, partition_key=project_id)
            if name:
                item["name"] = name
            if description:
                item["description"] = description
            item["updatedAt"] = datetime.utcnow().isoformat()

            container.replace_item(item=project_id, body=item)
            return Project(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                createdAt=item["createdAt"],
                updatedAt=item["updatedAt"]
            )
        except Exception:
            return None

    @strawberry.mutation
    def delete_project(self, info, project_id: str) -> bool:
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        try:
            container.delete_item(item=project_id, partition_key=project_id)
            return True
        except Exception:
            return False