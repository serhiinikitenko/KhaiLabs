import json
import sys

from pymongo import MongoClient

help_str = """
    use database <name>
    use collection <name>
    
    list database
    list collection
    
    list document
    list document {}
    
    add document {}
    add document [{}]
    
    update document {}
    update document [{}]
    
    delete document {}
    delete document [{}]
    
    exit
"""


def use_database(cmd, args):
    global database

    if len(args) == 0:
        print('Error: specify database name')
        return

    database = args[0]
    print(database + ' database in use')


def use_collection(cmd, args):
    global collection

    if database is None:
        print('Error: select database first: use database <name>')
        return

    if len(args) == 0:
        print('Error: specify collection name')
        return

    collection = args[0]
    print(collection + ' collection in use')


def list_database(cmd, args):
    for item in client.list_databases():
        print(item['name'])


def list_collection(cmd, args):
    if database is None:
        print('Error: select database first: use database <name>')
        return

    for item in client[database].list_collections():
        print(item['name'])


def list_document(cmd, args):
    if database is None:
        print('Error: select database first: use database <name>')
        return

    if collection is None:
        print('Error: select collection first: use collection <name>')
        return

    query = dict()
    if len(args) > 0:
        try:
            query = json.loads(args[0])
        except json.decoder.JSONDecodeError:
            print('Error: not valid query json string')
            return

    for document in client[database][collection].find(query):
        print(document)


def add_document(cmd, args):
    if database is None:
        print('Error: select database first: use database <name>')
        return

    if collection is None:
        print('Error: select collection first: use collection <name>')
        return

    if len(args) == 0:
        print('Error: specify document in json string format')
        return

    documents = list()
    try:
        document = json.loads(args[0])
    except json.decoder.JSONDecodeError:
        print('Error: not valid document json string')
        return

    if isinstance(document, list):
        documents.extend(document)

    if isinstance(document, dict):
        documents.append(document)

    result = client[database][collection].insert_many(documents)
    for item_id in result.inserted_ids:
        print(item_id)


def update_document(cmd, args):
    if database is None:
        print('Error: select database first: use database <name>')
        return

    if collection is None:
        print('Error: select collection first: use collection <name>')
        return

    if len(args) == 0:
        print('Error: specify document in json string format')
        return

    try:
        query = json.loads(args[0])
        update = json.loads(args[1])
    except json.decoder.JSONDecodeError:
        print('Error: not valid query or/and update json string')
        return

    result = client[database][collection].update_many(query, update)
    print('update count: ' + str(result.modified_count))


def delete_document(cmd, args):
    if database is None:
        print('Error: select database first: use database <name>')
        return

    if collection is None:
        print('Error: select collection first: use collection <name>')
        return

    try:
        query = json.loads(args[0])
    except json.decoder.JSONDecodeError:
        print('Error: not valid query json string')
        return

    result = client[database][collection].delete_many(query)
    print('deleted count: ' + str(result.deleted_count))


def help_cmd(cmd, args):
    print(help_str)


def exit_cmd(cmd, args):
    sys.exit(0)


cmd_handler_map = {
    ('use', 'database',): use_database,
    ('use', 'collection',): use_collection,
    ('list', 'database',): list_database,
    ('list', 'collection',): list_collection,
    ('list', 'document',): list_document,
    ('add', 'document',): add_document,
    ('update', 'document',): update_document,
    ('delete', 'document',): delete_document,
    ('help',): help_cmd,
    ('exit',): exit_cmd,
}


def error_handler(cmd, args):
    print('Error: not supported command: ' + ' '.join(cmd + args))


client = None
database = None
collection = None


def main():
    global client
    client = MongoClient('mongodb://root:example@127.0.0.1:27017')

    print('Enter a command to do something, e.g. `use database test`.')
    print('To get help, enter `help`.')

    while True:
        user_input = input('> ')
        user_input_args = tuple(user_input.split())

        if len(user_input_args) > 0:
            cmd = user_input_args[:2]
            args = user_input_args[2:]
            handler = cmd_handler_map.get(cmd, error_handler)
            handler(cmd, args)

        continue


if __name__ == "__main__":
    main()
