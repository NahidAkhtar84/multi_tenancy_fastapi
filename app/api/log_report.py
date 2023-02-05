from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.core.const import LOG_RECORDS_PATH

router = APIRouter()


@router.get("/logs/list")
def logs(
        db: Session = Depends(deps.get_db)
) -> List:
    log_file_directory = f"./{LOG_RECORDS_PATH}/logs.log"

    with open(log_file_directory) as file:
        file = file.readlines()
    response = [line for line in file]

    return response