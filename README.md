### Xeneta API Task

Created an API to fetch rates for various source and destination. The API is 
created with Python/Django.

The code is organized in 3 layers,

**VIEWS**: View layer will get encountered first in a request/response lifecycle. It is responsible for 
    - validating the request, 
    - fetching data from services
    - serialize the data and return a Response.

**SERVICES**: The service layer is responsible to fetch data from a repository
to some processing and return the result to the view. Views will not directly access the repository.


**REPOSOTORY**: This is the last layer in a request/response cycle, it is responsible to fetch data from the database and return the data to the service. This intermediate layer is usefull in a way, such that it abstracts away all the database communication. Right now it uses rawsql to communicate with the database, if tommorow we need an ORM, changes only needs to be made to this layer.



### SETUP
To setup the project:

- Clone the project.
- Run `docker-compose up`
    - The above command starts up two services,
        - **ratestask_api**
        - **ratestask_db**

- Go to http://localhost:8000/swagger, for trying out the API. Along with the response, the api also provides a **max_count** header, the total count of all the prices, for the given filters, that can be used by the client to show the page list.


### APIS

API: `/rates/`

METHOD: **GET**

RESPONSE: 
```json
[
  {
    "day": "2016-01-01",
    "average_price": 1463
  },
  {
    "day": "2016-01-02",
    "average_price": 1463
  },
  {
    "day": "2016-01-04",
    "average_price": null
  }
  ....
  {
    "day": "2016-01-31",
    "average_price": 1455
  }  
```

### USER_DEFINED_HEADERS:
`max_count`: Total count of all the prices, for the given filters.


### TestCases:
Sorry :( couldn't add testcases due to less time.


### Screenshots:

<img width="1422" alt="Screenshot 2022-11-28 at 20 58 48" src="https://user-images.githubusercontent.com/9046803/204369450-49db8ac2-e832-4e72-bb9d-d1ea665a0dd9.png">
<img width="1423" alt="Screenshot 2022-11-28 at 20 59 06" src="https://user-images.githubusercontent.com/9046803/204369479-5a483452-ae85-4b81-a928-f8b48fde09a2.png">


