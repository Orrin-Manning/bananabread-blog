from fastapi import FastAPI

app = FastAPI(title="bananabread.blog")


@app.get("/")
async def root():
    return {"message": "Welcome to bananabread.blog"}
