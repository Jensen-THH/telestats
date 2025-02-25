import uvicorn
from fastapi import FastAPI
from app.routes.messages import router as messages_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cấu hình CORS để frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Telegram Statistics API is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)