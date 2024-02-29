import asyncio
import psycopg2
import json

def connection():
    dbcon = psycopg2.connect(
        dbname = 'megafon',
        user = 'postgres',
        password = '934007717', 
        host = 'localhost'
    )

    dbcur = dbcon.cursor()
    return dbcon, dbcur

dbcon, dbcur = connection()

async def get_all_users(dbcur):
    dbcur.execute(
        '''
            SELECT * FROM users
        '''
    )
    users = dbcur.fetchall()
    json_users = []
    for user in users:
        user_dict = {
            'id': user[0],
            'last_name': user[1],
            'first_name': user[2],
            'phone_number': user[3],
            'balance': user[4]
        }
        json_users.append(user_dict)
    # print(json.loads(json.dumps(json_users[0]['last_name'])))
    return json.dumps(json_users)

async def get_user_by_id(dbcur, id):
    dbcur.execute(
        '''
            SELECT * FROM users
            WHERE id = %s
        ''',
        (id,)
    )
    user = dbcur.fetchall()
    user_dict = {
            'id': user[0][0],
            'last_name': user[0][1],
            'first_name': user[0][2],
            'phone_number': user[0][3],
            'balance': user[0][4]
    }
    return json.loads(json.dumps(user_dict))
    
async def create_new_user(dbcon, dbcur, last_name, first_name, phone_number, balance):
    dbcur.execute(
        '''
            INSERT INTO users(last_name, first_name, phone_number, balance)
            VALUES(%s, %s, %s, %s)
        ''',
        (last_name, first_name, phone_number, balance)
    )
    dbcon.commit()
    return {"status": 201, "msg": "User Created"}

async def get_all_services(dbcur):
    dbcur.execute(
        '''
            SELECT * FROM services
        '''
    )

    services = dbcur.fetchall()
    json_services = []
    for service in services:
        service_dict = {
            'id': service[0],
            'service_name': service[1],
            'service_price': service[2]
        }
        json_services.append(service_dict)
    return json.loads(json.dumps(json_services))

async def get_service_by_id(dbcur, id):
    dbcur.execute(
        '''
            SELECT * FROM services
            WHERE id = %s
        ''',
        (id,)
    )
    service = dbcur.fetchall()
    service_dict = {
        'id': service[0][0],
        'service_name': service[0][1],
        'service_price': service[0][2]
    }
    return json.loads(json.dumps(service_dict))

async def create_new_service(dbcon, dbcur, service_name, service_price):
    dbcur.execute(
        '''
            INSERT INTO services(service_name, service_price)
            VALUES(%s, %s)
        ''',
        (service_name, service_price)
    )
    dbcon.commit()
    return {'status': 201, "msg": 'Service Created'}

async def make_new_transfer(dbcon, dbcur, transfer, user, service):
    if transfer.isTransfered == 1:
        if user['balance'] > service['service_price']:
            dbcur.execute(
                '''
                    INSERT INTO transfers(users_id, service_id, isTransfered)
                    VALUES(%s, %s, %s)
                ''',
                (user['id'], service['id'], 1)
            )
            dbcon.commit()

            dbcur.execute(
                '''
                    UPDATE users SET balance = %s
                    WHERE id = %s
                ''',
                (user['balance'] - service['service_price'], user['id'])
            )
            dbcon.commit()
            return {'status': 201, 'msg': 'Made Transfer'}
        else:
            dbcon.rollback()
            return {'status': 403, 'msg': 'Transfer error'}
    else:
        if transfer.isTransfered == 0:
            dbcur.execute(
                '''
                    INSERT INTO transfers(users_id, service_id, isTransfered)
                    VALUES(%s, %s, %s)
                ''',
                (user['id'], service['id'], 0)
            )
            dbcon.commit()
            return {'status': 403, 'msg': 'Transfer Denied'}
        
async def get_all_transfers(dbcur):
    dbcur.execute(
        '''
            SELECT * FROM transfers
        '''
    )

    transfers = dbcur.fetchall()
    transfer_json = []
    for transfer in transfers:
        transfer_dict = {
            'id': transfer[0],
            'users_id': transfer[1],
            'service_id': transfer[2],
            'isTransfered': transfer[3]
        }
        transfer_json.append(transfer_dict)

    return json.loads(json.dumps(transfer_json))