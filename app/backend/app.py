from fastapi import FastAPI, UploadFile, File
import shutil, uuid
from inference import predict

app = FastAPI()

@app.post("/predict")
async def predict_sign(file: UploadFile = File(...)):
    path = f"/tmp/{uuid.uuid4()}.mp4"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"result": predict(path)}
