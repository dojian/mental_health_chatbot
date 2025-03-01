from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def get_health():
    '''
    Returns a status check indicating if the service is healthy.
    '''
    return {"status": "healthy"}

@app.get("/hello")
async def get_hello(name: str):
    '''
    Takes a parameter of name and returns a json object with the parameter.
    '''
    return {"message": f"Hello {name}"}