from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import uuid
import os
import logging
from inference import predict

# إعداد اللوجز (عشان نشوف الأخطاء في التيرمينال)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/predict")
async def predict_sign(file: UploadFile = File(...)):
    path = ""
    try:
        # 1. إنشاء اسم ملف فريد (بصيغة webm لأن ده اللي بيتبعت من المتصفح)
        filename = f"{uuid.uuid4()}.webm"
        path = f"/tmp/{filename}"
        
        logger.info(f"Receiving file request. Saving to {path}")
        
        # 2. حفظ الملف القادم من الفرونت
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # 3. التأكد من حجم الملف (عشان لو وصل فاضي نعرف)
        if not os.path.exists(path):
             logger.error("File path does not exist after write attempt!")
             raise HTTPException(status_code=500, detail="File save failed")

        file_size = os.path.getsize(path)
        logger.info(f"File saved successfully. Size: {file_size} bytes")

        if file_size == 0:
            logger.error("Received empty file")
            raise HTTPException(status_code=400, detail="Empty video file received")

        # 4. تشغيل الموديل (Inference)
        logger.info("Starting prediction...")
        result = predict(path)
        logger.info(f"Prediction success. Result: {result}")
        
        # 5. تنظيف (مسح الفيديو المؤقت)
        os.remove(path)
        
        return {"result": result}

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        
        # محاولة مسح الملف لو حصل خطأ وهو لسه موجود
        if path and os.path.exists(path):
            os.remove(path)
            
        # إرجاع تفاصيل الخطأ للفرونت
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")