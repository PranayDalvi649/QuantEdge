from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze

app = FastAPI(title="QuantEdge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/analyze")
def get_analysis(ticker: str):
    result = analyze(ticker)
    if "error" in result:
        return {"error": result["error"]}
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
