import os
import uuid
import shutil
from typing import List
from fastapi import File, UploadFile, HTTPException
from starlette import status
from app.core.log_config import logger


ALLOWED_FILE_EXTENSIONS = ['pdf']
COUNTRY_FILE_UPLOAD_PATH = 'media/country'


def file_upload(
        uploaded_file: UploadFile,
        upload_path: str,
        ALLOWED_FILE_EXTENSIONS: List = ALLOWED_FILE_EXTENSIONS,
) -> str:
    filename = uploaded_file.filename
    split_file_name = os.path.splitext(filename)
    file_extension = split_file_name[1].split(".")[-1]
    if file_extension.lower() not in ALLOWED_FILE_EXTENSIONS:
        logger.error(f"File type must be one of {', '.join(ALLOWED_FILE_EXTENSIONS)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type must be one of {', '.join(ALLOWED_FILE_EXTENSIONS)}",
        )
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    file_location = f"{upload_path}/{filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(uploaded_file.file, file_object)
    return file_location
