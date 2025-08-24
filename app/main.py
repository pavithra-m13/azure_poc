from fastapi import FastAPI
from gql.schema import graphql_app

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
def health():
    return {"status": "ok"}