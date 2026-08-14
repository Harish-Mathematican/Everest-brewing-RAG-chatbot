import uvicorn
import os

if __name__ == "__main__":
    print("Starting Everest Brewing RAG AI Server & Operations Dashboard...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
