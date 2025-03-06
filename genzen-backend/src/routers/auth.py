from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login(username: str, password: str):
    '''
    Takes a username and password and returns a json object with the username.
    '''
    return {"username": username, "message": "You have been logged in."}

@router.post("/logout")
async def logout(username: str):
    '''
    Takes a username and returns a json object with the username.
    '''
    return {"username": username, "message": "You have been logged out."}