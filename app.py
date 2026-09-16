import os
import shutil
import tempfile
from pathlib import Path
from starlette.background import BackgroundTask

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pdf2docx import Converter
from docx import Document

MAX_FILE_SIZE = 25 * 1024 * 1024
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "").split(",") if x.strip()]

app = FastAPI(title="PDF to DOCX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def cleanup(path: Path):
    shutil.rmtree(path, ignore_errors=True)

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    filename = file.filename or "document.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    temp_dir = Path(tempfile.mkdtemp(prefix="pdf2docx_"))
    pdf_path = temp_dir / "input.pdf"
    docx_path = temp_dir / "converted.docx"

    try:
        size = 0
        with pdf_path.open("wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="The PDF is larger than the 25 MB limit.")
                output.write(chunk)

        try:
            converter = Converter(str(pdf_path))
            converter.convert(str(docx_path))
            converter.close()
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail="The PDF could not be converted. It may be damaged or use unsupported content."
            ) from exc

        try:
            doc = Document(str(docx_path))
            doc.core_properties.author = "python-docx"
            doc.save(str(docx_path))
        except Exception as exc:
            raise HTTPException(status_code=500, detail="The DOCX metadata could not be updated.") from exc

        return FileResponse(
            str(docx_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=Path(filename).stem + ".docx",
            background=BackgroundTask(cleanup, temp_dir),
        )

    except HTTPException:
        cleanup(temp_dir)
        raise
    except Exception as exc:
        cleanup(temp_dir)
        raise HTTPException(status_code=500, detail="Unexpected conversion error.") from exc
