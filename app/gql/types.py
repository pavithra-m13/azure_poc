import strawberry

@strawberry.type
class Project:
    id: str
    name: str
    description: str
    createdAt: str
    updatedAt: str