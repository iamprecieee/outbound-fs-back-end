from fastapi import FastAPI
from app.config.config import settings
from app.utils.esl import ESLConnection
from app.routers import calls, status

app = FastAPI(title="FreeSWITCH API", version="0.1.0")

# Include routers
app.include_router(calls.router)
app.include_router(status.router)

@app.get("/")
async def root():
    return {"message": "FreeSWITCH API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 
