from fastapi import APIRouter

router = APIRouter()

@router.get('/hello', tags=["General"])
def read_hello():
    return {"message": "Hello World"}
