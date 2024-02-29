from fastapi import FastAPI

# async database
from repository.DatabaseAsync import DatabaseSession, create_connection
from repository.DatabaseAsync import get_all_users, get_user_by_id, create_new_user
from repository.DatabaseAsync import get_services, get_service_by_id
from repository.DatabaseAsync import make_new_transfer, get_all_transfers, get_denied_transfers, get_accepted_transfers
from repository.DatabaseAsync import get_transfer_by_users_id

from test import request_to_service, second_request

from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

database = DatabaseSession('postgres', '934007717', 'megafon', 'localhost')
database2 = DatabaseSession('postgres', '934007717', 'megafon2', 'localhost')

class UserIn(BaseModel):
    last_name: str
    first_name: str
    phone_number: str
    balance: int

class UsersOut(BaseModel):
    id: int
    last_name: str
    first_name: str
    phone_number: str
    balance: int

class ServicesOut(BaseModel):
    id: int
    service_name: str
    service_price: int

class ServiceIn(BaseModel):
    service_name: str
    service_price: int

class TransferIn(BaseModel):
    users_id: int
    service_id: int
    isTransfered: int

class TransferOut(BaseModel):
    id: int
    users_id: int
    service_id: int
    isTransfered: int


@app.on_event('startup')
async def startup_event():
    global db_session1
    global db_session2
    db_session1 = await create_connection(database)
    db_session2 = await create_connection(database2)

@app.get('/api/users', response_model=List[UsersOut])
async def get_users():
    users = await get_all_users(db_session1)
    return users

@app.get('/api/user/{users_id}', response_model=UsersOut)
async def get_user(users_id):
    user = await get_user_by_id(db_session1, users_id)
    return user

@app.post('/api/new_user')
async def new_user(user: UserIn):
    await create_new_user(db_session1, user)
    return {'status': 201, 'msg': 'User Created'}

@app.post('/api/new_transfer')
async def new_transfer(transfer: TransferIn):
    user = await get_user_by_id(db_session1, transfer.users_id)
    service = await get_service_by_id(db_session1, transfer.service_id)
    await make_new_transfer(db_session1, db_session2, user, service, transfer)
    return transfer

@app.get('/api/transfers', response_model=List[TransferOut])
async def get_transfers():
    transfers = await get_all_transfers(db_session2)
    return transfers

@app.get('/api/get_denied_transfers', response_model=List[TransferOut])
async def denied_transfers():
    transfers = await get_denied_transfers(db_session2)
    return transfers

@app.get('/api/get_accepted_transfers', response_model=List[TransferOut])
async def accepted_transfers():
    transfers = await get_accepted_transfers(db_session2)
    return transfers

@app.get('/api/get_users_transfers/{users_id}')
async def get_users_transfers(users_id: int):
    transfers = await get_transfer_by_users_id(db_session1, db_session2, users_id)
    return transfers

@app.get('/api/requests/get_weather_dushanbe')
async def get_weather():
    weather_json = await request_to_service()
    return weather_json

@app.get('/api/jsonholder')
async def get_api(id):
    response = await second_request(id)
    return response