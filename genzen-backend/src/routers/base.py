from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_root():
    '''
    Returns a welcome message.
    '''
    return {"message": "Welcome to the GenZen Root Backend!"}

@router.get("/health")
async def get_health():
    '''
    Returns a status check indicating if the service is healthy.
    '''
    return {"status": "healthy"}

@router.get("/hello")
async def get_hello(name: str):
    '''
    Takes a parameter of name and returns a json object with the parameter.
    '''
    return {"message": f"Hello {name}"}