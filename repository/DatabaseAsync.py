import asyncio
import asyncpg
import json

class DatabaseSession:
    def __init__(self, user: str, password: str, database: str, host: str):
        self.user = user
        self.password = password
        self.database = database
        self.host = host

async def create_connection(database):
    dbcon = await asyncpg.connect(
        user = database.user,
        password = database.password,
        database = database.database,            
        host = database.host
    )

    return dbcon

async def get_all_users(database_session):
    users = await database_session.fetch(
        '''
            SELECT * FROM users
        '''
    )
    users_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'last_name': user[1],
            'first_name': user[2],
            'phone_number': user[3],
            'balance': user[4]
        }
        users_list.append(user_dict)
    return json.loads(json.dumps(users_list))
    
async def get_user_by_id(db_session, user_id):
    user = await db_session.fetchrow(
        f'''
            SELECT * FROM users
            WHERE id = {user_id}
        ''',
    )
    user_dict = {
        'id': user[0],
        'last_name': user[1],
        'first_name': user[2],
        'phone_number': user[3],
        'balance': user[4]
    }

    return json.loads(json.dumps(user_dict))

async def create_new_user(db_session, user):
    await db_session.execute(
        f'''
            INSERT INTO users(last_name, first_name, phone_number, balance)
            VALUES($1, $2, $3, $4)
        ''', user.last_name, user.first_name, user.phone_number, user.balance
    )

async def get_services(db_session):
    services = await db_session.fetch(
        '''
            SELECT * FROM services
        '''
    )

    services_list = []
    for service in services:
        service_dict = {
            'id': service[0],
            'service_name': service[1],
            'service_price': service[2]
        }
        services_list.append(service_dict)

    return json.loads(json.dumps(services_list))

async def get_service_by_id(db_session, service_id):
    service = await db_session.fetchrow(
        f'''
            SELECT * FROM services
            WHERE id = {service_id}
        '''
    )

    service_dict = {
        'id': service[0],
        'service_name': service[1],
        'service_price': service[2]
    }

    return json.loads(json.dumps(service_dict))

async def make_new_transfer(db_session1, db_session2, user, service, transfer):
    if transfer.isTransfered == 1:
        await db_session2.execute(
            '''
                INSERT INTO transfers(users_id, services_id, isTransfered)
                VALUES($1, $2, $3)
            ''', user['id'], service['id'], 1 
        )

        await db_session1.execute(
            '''
                UPDATE users SET balance = $1
                WHERE id = $2
            ''', (user['balance'] - service['service_price']), user['id']
        )
    elif transfer.isTransfered == 0:
        await db_session2.execute(
            '''
                INSERT INTO transfers(users_id, services_id, isTransfered)
                VALUES($1, $2, $3)
            ''', user['id'], service['id'], 0
        )

async def get_all_transfers(db_session):
    transfers = await db_session.fetch(
        '''
            SELECT * FROM transfers
        '''
    )
    transfers_json = await all_transfers_to_json(transfers)
    return transfers_json

async def get_denied_transfers(db_session):
    transfers = await db_session.fetch(
            '''
                SELECT * FROM transfers
                WHERE isTransfered = 0
            '''
        )
    transfers_json = await all_transfers_to_json(transfers)
    return transfers_json

async def get_accepted_transfers(db_session):
    transfers = await db_session.fetch(
            '''
                SELECT * FROM transfers
                WHERE isTransfered = 1
            '''
        )
    transfers_json = await all_transfers_to_json(transfers)
    return transfers_json

async def async_append(data, data_json):
    data_json.append(data)

async def all_transfers_to_json(transfer_list):
    transfer_json = []

    for transfer in transfer_list:
        transfer_dict = {
            'id': transfer[0],
            'users_id': transfer[1],
            'service_id': transfer[2],
            'isTransfered': transfer[3]
        }
        await async_append(transfer_dict, transfer_json)
    return json.loads(json.dumps(transfer_json))

async def get_transfer_by_users_id(db_session1, db_session2, users_id):
    user_data = await get_user_by_id(db_session1, users_id)

    transfers = await db_session2.fetch(
        '''
            SELECT * FROM transfers
            WHERE users_id = $1
        ''', users_id,
    )

    user_transfer_data = []
    user = {
        'user': {
            'id': user_data['id'],
            'last_name': user_data['last_name'],
            'first_name': user_data['first_name'],
            'phone_number': user_data['phone_number'],
            'balance': user_data['balance']
        },
        'transfers': []
    }   
    for transfer in transfers:
        user['transfers'].append({
            'id': transfer[0],
            'service_id': transfer[2],
            'isTransfered': transfer[3]
        })
    await async_append(user, user_transfer_data)

    return json.loads(json.dumps(user_transfer_data))