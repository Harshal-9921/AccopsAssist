from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from admin.auth import verify_admin
from analytics.reader import usage_summary, top_questions

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/usage-summary")
def get_usage_summary(admin=Depends(verify_admin)):
    return usage_summary()

@router.get("/top-questions")
def get_top_questions(admin=Depends(verify_admin)):
    return {"top_questions": top_questions()}

@router.get("/download-csv")
def download_csv(admin=Depends(verify_admin)):
    return FileResponse(
        path="data/usage_logs.csv",   # ✅ FIXED PATH
        filename="usage_logs.csv",
        media_type="text/csv"
    )
