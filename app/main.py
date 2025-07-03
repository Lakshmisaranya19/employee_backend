from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def root():
    return {"message": "Hello, from FAST API!"}