from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import MathStepRequest, MathStepResponse
from app.agent import verify_math_step
from app.image_reader import extract_math_from_image


app = FastAPI(
    title="Math Step Verification Agent",
    description="Verifies incomplete math steps using SymPy and supports text/image input.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/verify-step", response_model=MathStepResponse)
def verify_step(request: MathStepRequest):
    return verify_math_step(request)


@app.post("/verify-image", response_model=MathStepResponse)
async def verify_image(
    file: UploadFile = File(...),
    problem_type: str = Form("integration"),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    try:
        image_bytes = await file.read()

        if len(image_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image too large. Please upload an image under 5MB.",
            )

        extracted = extract_math_from_image(image_bytes, file.content_type)

        request = MathStepRequest(
            problem_type=problem_type,
            original_expression=extracted["original_expression"],
            partial_work=extracted["partial_work"],
            remaining_expression=extracted["remaining_expression"],
            variable=extracted.get("variable", "x"),
            substitution=extracted.get("substitution"),
        )

        response = verify_math_step(request)
        response.detected_text = extracted.get("partial_work")

        return response

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))