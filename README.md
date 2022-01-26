# internal-backend-worker

##Overview

Worker server do tests with url. All tests in `tests` directory.

## Points

---
#### /status
Return status server information

Method - GET

Results
1. If requests aren't authorization - `{"message": "Access is denied", "code": 403}`
2. Success
```json
{"queue": {"processed": 0,"in_progress": 0,"in_queue": 0,"average_processing_time": 0}}
```
---
#### /add-job
Add new job

Method - POST
```json
{
  "job": {
    "url": "www.daniliants.com",
    "id": 23424,
    "priority": "normal",
    "callback": "https://master.domain.com/callback/ID/TOKEN"
  }
}
```
Results
1. If requests aren't authorization - `{"message": "Access is denied", "code": 403}`
2. If method's GET - `{"message": "Method GET not allowed", "code": 400}`
3. Success
```json
{"message": "Job has been added", "code": 201}
```
---

##Tests

###Files Structure

- tests
  - first_test
    - tests.py
  - second_test
    - tests.py


###Example
All tests are in the folder - `tests`

example `tests.py` in `first_test` folder:
```python
class first_test:

    def __init__(self):
        pass
    
    def test_title(self, url):
        from bs4 import BeautifulSoup
        import requests
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features="lxml")
        title = soup.title.string
        return title
    
    def test_task_name(self, url):
        results = do_something(url)
        return result
```
Result:
```json
{
  "job": {
    "id": "23213",
    "url": "www.daniliants.com",
    "creation_date": "1640358505",
    "processing_time": 22
  },
  "results": {
    "first_test": {
      "test_title": "result value",
      "test_task_name": "result something"
    },
    ...
  }
}
```
####Rules
1. Class name must be same as parent folder name.
2. All methods must start name as 'test_'
3. All methods must return one argument.



---
##Development
Clone this repository to working directory.

Change Database access in `.env.dev` and `docker-compose.yml`. (optional)

Build containers - use command `docker-compose build`

Run containers - use command `docker-compose up` or `docker-compose up -d` for use demon 
mode.

Check localhost - 0.0.0.0:5000

If you change files - rebuild containers with commands `docker-compose down` or `docker-compose down -v`
if you want clear database and other files' server. Compile containers `docker-compose build` and 
run `docker-compose up`.

If you want to check logs - use command `docker-compose logs -f`

---

##Deploy
Firstly need generate ssh key - use command `ssh-keygen`.
Add key to repository settings, tab `Deploy keys`.

1. Clone repository to ubuntu user directory.
2. Go to project folder
3. Go to `deploy` folder
4. Use command `chmod +x ./setup` - its script install Docker and another system packages.
5. Run `./setup`
6. Go to project folder

Change database accesses to production in files `.env.prod`:
- DB_NAME
- DB_USER
- DB_PASS

Change database accesses to production in files `docker-compose.prod.yml`:
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

Build server `sudo docker-compose -f docker-compose.prod.yml build`.

Run server `sudo docker-compose -f docker-compose.prod.yml up -d`.

If you have change files - follow commands:

`sudo docker-compose -f docker-compose.prod.yml down` - stop containers without 
clearing volumes (database will not remove)

`sudo docker-compose -f docker-compose.prod.yml down -v` - stop containers with 
clearing volumes (database will remove)

`sudo docker-compose -f docker-compose.prod.yml build` - build containers with new files updates

`sudo docker-compose -f docker-compose.prod.yml up -d` - run server

Create backup database before any actions with docker containers.
