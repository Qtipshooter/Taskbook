import requests
import json

# this will change if tests are ran in prod or dev environment
host = 'http://0.0.0.0:5000/'

# any legitimate credentials are needed for the tests to pass
creds = {
    'user_email': 'default@gmail.com',
    'user_password': 'password'
}

test_create_task = {
    'description': "This is a test task",
    'date': "2022-02-15",
    'time': "12:30"
}

test_update_task = {
    'id': 5,
    'description': "This should be updated",
    'completed': False,
    'date': "2022-02-15",
    'time': "10:20"
}

def test_get_tasks():
    # creates session
    with requests.Session() as s:
        s.post(host + 'login', data=creds)

        # calls the get tasks function in API
        get_tasks = s.get(host + '/api/tasks')
        assert get_tasks.status_code == 200

def test_create_tasks():
    with requests.Session() as s:
        s.post(host + '/login', data=creds)

        # calls the create task function from API
        post_tasks = s.post(host + '/api/tasks', json=test_create_task)
        assert post_tasks.status_code == 200

def test_update_tasks():
    with requests.Session() as s:
        s.post(host + '/login', data=creds)

        # calls the update task function from API
        put_tasks = s.put(host + '/api/tasks', json=test_update_task)
        assert put_tasks.status_code == 200

def test_delete_tasks():
    with requests.Session() as s:
        s.post(host + '/login', data=creds)  

        # calls the delete task function from API
        delete_tasks = s.delete(host + '/api/tasks', json={'id': 5})
        assert delete_tasks.status_code == 200

test_get_tasks()
test_create_tasks()
test_update_tasks()
test_delete_tasks()