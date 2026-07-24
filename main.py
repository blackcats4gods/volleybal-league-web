from fastapi import FastAPI

app = FastAPI(title="Volleyball League API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Volleyball League API is running"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}
