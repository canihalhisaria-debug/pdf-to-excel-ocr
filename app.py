import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from converter import ConversionError, convert_file_to_excel

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp"}

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = "pdf-to-excel-ocr-secret"


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        upload = request.files.get("file")

        if upload is None or upload.filename == "":
            flash("Please choose a PDF or image file.")
            return redirect(url_for("index"))

        if not is_allowed_file(upload.filename):
            flash("Unsupported file type. Upload PDF or image files only.")
            return redirect(url_for("index"))

        filename = f"{uuid4().hex}_{secure_filename(upload.filename)}"
        upload_path = UPLOAD_DIR / filename
        upload.save(upload_path)

        output_path = OUTPUT_DIR / f"{upload_path.stem}.xlsx"

        try:
            result = convert_file_to_excel(upload_path, output_path)
        except ConversionError as exc:
            flash(f"Conversion failed: {exc}")
            return redirect(url_for("index"))

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{Path(result['source_file']).stem}.xlsx",
        )

    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
