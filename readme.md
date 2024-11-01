  # Alternova
API for grade and subject management, where teachers and students can manage their academic responsibilities.

# Instructions for running and testing the API.

### 1. Prerequisites

Make sure you have installed:
- **Python 3.8+**


### 2. Setting up the Environment

1. **Clone the project repository** to your local machine:
    ```bash
    git clone https://github.com/Spoilt83/Alternova-API.git
    cd <nombre-del-proyecto>
    ```

2. **Create a virtual environment** and activate it:
    ```bash
    python3 -m venv env
    source env/bin/activate  #In Windows use `env\Scripts\activate`
    ```

3. **Install the project dependencies** listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Database Configuration

1. **Apply migrations** to create the tables in the database:
    ```bash
    python manage.py makemigrations
    ```
    ```bash
    python manage.py migrate
    ```

2. **Create a superuser** to access the Django admin panel:
    ```bash
    python manage.py createsuperuser
    ```
### 4. Running the Development Server

Start the development server with the following command:

   
    python manage.py Runserver
    

# Database Structure

## Table `User`
This model extends Django's base user model (`AbstractUser`) to include `email` as a primary identifier and to encrypt `username` and `password`.

| Field Name | Data type      | Description                                     | Restrictions              |
|------------------|--------------------|-------------------------------------------------|----------------------------|
| `id`             | INT                | Unique user identifier                 | PK, AUTO_INCREMENT         |
| `email`          | VARCHAR(255)       | User email                  | UNIQUE, NOT NULL           |
| `username`       | VARCHAR(150)       | Username (encrypted)                  | UNIQUE, NOT NULL           |
| `is_active`      | BOOLEAN            | Indicates whether the user is active                | DEFAULT TRUE               |
| `date_joined`    | TIMESTAMP          | User creation date                   | AUTO_GENERATED             |
| `last_login`     | TIMESTAMP          | Last login date               | AUTO_GENERATED             |

---

## Table `Student`
This model represents students, linked one-to-one to the `User` model and contains fields specific to the student profile.

| Field Name | Data Type       | Description                                     | Restrictions             |
|------------------|--------------------|-------------------------------------------------|----------------------------|
| `id`             | INT                | Unique student identifier              | PK, AUTO_INCREMENT         |
| `user_id`        | FK a `User`        | User associated with the student                  | UNIQUE, NOT NULL           |
| `student_id`     | VARCHAR(20)        | Student ID Number            | UNIQUE, NOT NULL           |
| `career`         | VARCHAR(100)       | Career that studies                             | NOT NULL                   |
| `semester`       | INT                | Student's current semester                  | MIN: 1, MAX: 12            |

---

## Table `Professor`
This model represents teachers, with specific information about their profile and a one-to-one relationship with `User`.

| Field Name | Data Type       | Description                                     | Restrictions              |
|------------------|--------------------|-------------------------------------------------|----------------------------|
| `id`             | INT                | Unique teacher identifier                | PK, AUTO_INCREMENT         |
| `user_id`        | FK a `User`        | User associated with the teacher                    | UNIQUE, NOT NULL           |
| `professor_id`   | VARCHAR(20)        | Teacher ID Number           | UNIQUE, NOT NULL           |
| `department`     | VARCHAR(100)       | Department to which it belongs                   | NOT NULL                   |
| `title`          | VARCHAR(100)       | Academic title                                | NOT NULL                   |
| `specialization` | VARCHAR(200)       | Area of ​​specialization                         | NOT NULL                   |

---

## Table `Subject`
This table stores information about available subjects, with the option to define prerequisites and an assigned teacher.

| Field Name | Data Type       | Description                                    | Restrictions              |
|------------------|--------------------|-------------------------------------------------|----------------------------|
| `id`             | INT                | Unique identifier of the subject               | PK, AUTO_INCREMENT         |
| `name`           | VARCHAR(100)       | Name of the subject                            | NOT NULL                   |
| `code`           | VARCHAR(20)        | Unique subject code                      | UNIQUE                     |
| `description`    | TEXT               | Description of the subject                       |                             |
| `credits`        | INT                | Number of credits                              | MIN: 1                     |
| `prerequisites`  | M2M con `Subject`  | Subjects that are prerequisites             |                             |
| `professor_id`   | FK a `Professor`   | Assigned teacher                               | NULLABLE                   |
| `department`     | VARCHAR(100)       | Department of the subject                      |                             |
| `semester_number`| INT                | Suggested semester                               | MIN: 1, MAX: 12            |
| `is_active`      | BOOLEAN            | Indicates whether the subject is active                | DEFAULT TRUE               |

---

## Table `Enrollment`
This model records the enrollment of students in specific subjects and their progress status. Each enrollment has a reference to `Student`, `Subject` y `Professor`.

| Field Name | Data Type       | Description                                     | Restrictions                          |
|------------------|--------------------|-------------------------------------------------|----------------------------------------|
| `id`             | INT                | Unique registration identifier           | PK, AUTO_INCREMENT                     |
| `student_id`     | FK a `Student`     | Enrolled student                             | NOT NULL                               |
| `subject_id`     | FK a `Subject`     | Subject in which it is registered                 | NOT NULL                               |
| `professor_id`   | FK a `Professor`   | Professor who teaches the subject                 | DEFAULT 1                              |
| `status`         | CHAR(2)            | Registration status (`PE`, `AC`, `CO`, `CA`)| DEFAULT: 'PE'                          |
| `grade`          | FLOAT              | Final grade                              | MIN: 0.0, MAX: 5.0                     |
| `attendance`     | FLOAT              | Attendance percentage                        | MIN: 0.0, MAX: 100.0                   |
| `date_enrolled`  | TIMESTAMP          | Registration date                            | AUTO_GENERATED                         |
| `date_completed` | TIMESTAMP          | End date                           | NULLABLE                               |
| `is_completed`   | BOOLEAN            | Indicates whether the registration is complete          | DEFAULT FALSE                          |
| `semester_period`| VARCHAR(20)        | Semester period (Example: "2024-1")        | DEFAULT "2024-1"                       |
| `notes`          | TEXT               | Additional notes                               | NULLABLE                               |

### Relations

- **`Student` y `Enrollment`**:One-to-many relationship. A student can have many enrollments, but each enrollment belongs to only one student..
- **`Professor` y `Subject`**: One-to-many relationship. A teacher can teach multiple subjects, but each subject has an assigned teacher.
- **`Subject` y `Prerequisites`**:Many-to-many relationship, since one subject may require several subjects as prerequisites and may be a requirement for several others.
- **`Enrollment`**: One to many relationship with `Student`, `Subject` y `Professor`. Each enrollment is unique to a combination of student, subject, and semester period.(`semester_period`).


# Description of API routes and endpoints

## End-point: Token Authentication
### Create Token

This endpoint allows the user to obtain a token by providing their username, password, and email in the request body.

**Request Body**

- `username` (string): The username of the user.
    
- `password` (string): The password of the user.
    
- `email` (string): The email of the user.
    

**Response**

- Status: 200 OK
    
- Content-Type: application/json
    
- `refresh` (string): The refresh token.
    
- `access` (string): The access token.
### Method: POST
>```
>http://localhost:8000/api/token/
>```
### Body (**raw**)

```json
{
    "username": "profesor1",
    "password": "test123",
		"email": "profesor1@gmail.com"
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Refresh Token
### Refresh Token

This endpoint is used to refresh the access token by providing a valid refresh token.

#### Request Body

- `refresh` (string): A JSON Web Token (JWT) representing the refresh token.
    

#### Response

Upon successful execution, the server responds with a status code of 200 and a JSON object containing the new access token.

Example:

``` json
{
    "access": "new_access_token"
}

 ```
### Method: POST
>```
>http://localhost:8000/api/token/refresh/
>```
### Body (**raw**)

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMDU2MTM5NywiaWF0IjoxNzMwNDc0OTk3LCJqdGkiOiI0NWQ0ZjliODNmMzQ0ZTdlYmJiZjAwMmYzZWE1NTgwMiIsInVzZXJfaWQiOjJ9.HI-T15QNG7KekG544cpGmKy6SQmGW5rVSKWVDDuXvqs"
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 1. Un estudiante se inscribe en una lista de materias.
### Enroll Subjects

This endpoint allows the student to enroll in subjects.

#### Request Body

- `subject_ids` (array of integers) - The IDs of the subjects the student wants to enroll in.
    

#### Response

The response is in JSON format and includes a schema for the response.

``` json
{
    "type": "object",
    "properties": {
        "errors": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}

 ```
### Method: POST
>```
>http://localhost:8000/api/student/enroll_subjects/
>```
### Body (**raw**)

```json
{
    "subject_ids": [5, 6]
}
```

### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc1Mjk3LCJpYXQiOjE3MzA0NzQ5OTcsImp0aSI6Ijk2ODU1NTVkNDI2MDQ5MDNiMjM2MzdmY2E2ZmU0NzYxIiwidXNlcl9pZCI6Mn0.bn2-8uOGacZGRAwZ8tSg-avIHUaom2nq0a_Jb2iPKl0|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 2. Un estudiante puede obtener la lista de materias en las que está inscrito.
This endpoint makes an HTTP GET request to retrieve the subjects of the current student. The request does not include a request body. The response will be in JSON format with an array of objects containing information about the subjects. Each object includes attributes such as id, status, grade, attendance, date enrolled, date completed, is completed, semester period, notes, student, subject, and professor.
### Method: GET
>```
>http://localhost:8000/api/student/my_subjects/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc1NzQ5LCJpYXQiOjE3MzA0NzQ5OTcsImp0aSI6ImQ4NTNiMTJlYjFiYTQ0MmM5M2QzZjg3MTQ3ZWRlNzZhIiwidXNlcl9pZCI6Mn0.xRB4qO7nk8RIOulfM8EDuPhpqkA90Ak3IY08QBV_e5U|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 3. Un estudiante aprueba una materia con una nota igual o mayor a 3.0.
### Get Approved Subjects

This endpoint retrieves a list of approved subjects for a student.

#### Request Body

This is a GET request and does not require a request body.

#### Response Body

- `subjects` (array): An array of approved subjects containing the following attributes:
    
    - `id` (integer): The unique identifier for the subject.
        
    - `status` (string): The status of the subject.
        
    - `grade` (integer): The grade obtained in the subject.
        
    - `attendance` (integer): The attendance percentage for the subject.
        
    - `date_enrolled` (string): The date when the subject was enrolled.
        
    - `date_completed` (string): The date when the subject was completed.
        
    - `is_completed` (boolean): Indicates if the subject is completed.
        
    - `semester_period` (string): The period/semester during which the subject was completed.
        
    - `notes` (string): Any additional notes related to the subject.
        
    - `student` (integer): The ID of the student associated with the subject.
        
    - `subject` (integer): The ID of the subject.
        
    - `professor` (integer): The ID of the professor associated with the subject.
        
- `average` (integer): The average grade obtained in the approved subjects.
    

#### Example

``` json
{
    "subjects": [
        {
            "id": 1,
            "status": "Approved",
            "grade": 85,
            "attendance": 92,
            "date_enrolled": "2022-01-15",
            "date_completed": "2022-05-20",
            "is_completed": true,
            "semester_period": "Spring 2022",
            "notes": "Excellent performance",
            "student": 123,
            "subject": 456,
            "professor": 789
        }
    ],
    "average": 87
}

 ```
### Method: GET
>```
>http://localhost:8000/api/student/approved_subjects/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc1NzQ5LCJpYXQiOjE3MzA0NzQ5OTcsImp0aSI6ImQ4NTNiMTJlYjFiYTQ0MmM5M2QzZjg3MTQ3ZWRlNzZhIiwidXNlcl9pZCI6Mn0.xRB4qO7nk8RIOulfM8EDuPhpqkA90Ak3IY08QBV_e5U|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 4. Un estudiante puede obtener la lista de sus materias aprobadas y su promedio de puntaje general.
### Get Approved Subjects

This endpoint retrieves the list of approved subjects for a student.

#### Request

- Method: GET
    
- URL: `http://localhost:8000/api/student/approved_subjects/`
    

#### Response

- Status: 200
    
- Content-Type: application/json
    

##### Response Body

``` json
{
    "subjects": [
        {
            "id": 0,
            "status": "",
            "grade": 0,
            "attendance": 0,
            "date_enrolled": "",
            "date_completed": "",
            "is_completed": true,
            "semester_period": "",
            "notes": "",
            "student": 0,
            "subject": 0,
            "professor": 0
        }
    ],
    "average": 0
}

 ```
### Method: GET
>```
>http://localhost:8000/api/student/approved_subjects/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc1NzQ5LCJpYXQiOjE3MzA0NzQ5OTcsImp0aSI6ImQ4NTNiMTJlYjFiYTQ0MmM5M2QzZjg3MTQ3ZWRlNzZhIiwidXNlcl9pZCI6Mn0.xRB4qO7nk8RIOulfM8EDuPhpqkA90Ak3IY08QBV_e5U|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 5. Comprobar las materias que un estudiante ha reprobado
### GET /api/student/failed_subjects/

This endpoint retrieves a list of failed subjects for a student.

#### Request

No request body is required for this endpoint.

#### Response

The response is a JSON array containing objects with the following properties:

- `id` (number): The unique identifier for the failed subject.
    
- `status` (string): The status of the failed subject.
    
- `grade` (number): The grade obtained in the failed subject.
    
- `attendance` (number): The attendance percentage for the failed subject.
    
- `date_enrolled` (string): The date when the student enrolled for the subject.
    
- `date_completed` (string): The date when the subject was completed.
    
- `is_completed` (boolean): Indicates if the subject is completed or not.
    
- `semester_period` (string): The semester period during which the subject was taken.
    
- `notes` (string): Any additional notes related to the failed subject.
    
- `student` (number): The unique identifier of the student associated with the failed subject.
    
- `subject` (number): The unique identifier of the subject.
    
- `professor` (number): The unique identifier of the professor associated with the failed subject.
    

Example Response Body:

``` json
[
    {
        "id": 0,
        "status": "",
        "grade": 0,
        "attendance": 0,
        "date_enrolled": "",
        "date_completed": "",
        "is_completed": true,
        "semester_period": "",
        "notes": "",
        "student": 0,
        "subject": 0,
        "professor": 0
    }
]

 ```
### Method: GET
>```
>http://localhost:8000/api/student/failed_subjects/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc2MTE1LCJpYXQiOjE3MzA0NzQ5OTcsImp0aSI6IjQyNjI4MWI1MGFkNTQ5MmJiOGFiNzZiY2RmZWEwYjNlIiwidXNlcl9pZCI6Mn0.TbWEaIZbzr7H1FJqiGWczSFoEQRywxV6dHClttiac-g|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 6. Un profesor puede tener asignadas varias materias
This endpoint retrieves a list of professors from the API.

### Request

No request body is required for this GET request.

- HTTP Method: GET
    
- Endpoint: [http://localhost:8000/api/professor/](http://localhost:8000/api/professor/)
    

### Response

The response will be in JSON format with the following fields:

- `id` (number): The unique identifier for the professor
    
- `name` (string): The name of the professor
    
- `code` (string): The code associated with the professor
    
- `description` (string): A brief description of the professor
    
- `credits` (number): The credits assigned to the professor
    
- `department` (string): The department to which the professor belongs
    
- `semester_number` (number): The semester number
    
- `is_active` (boolean): Indicates if the professor is active
    
- `professor` (number): The unique identifier of the professor
    
- `prerequisites` (array): An array of prerequisites for the professor
    

Example Response:

``` json
[
    {
        "id": 0,
        "name": "",
        "code": "",
        "description": "",
        "credits": 0,
        "department": "",
        "semester_number": 0,
        "is_active": true,
        "professor": 0,
        "prerequisites": []
    }
]

 ```
### Method: GET
>```
>http://localhost:8000/api/professor/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc2NDIzLCJpYXQiOjE3MzA0NzYxMjMsImp0aSI6Ijk3YmY0NzAzYWZiYzQ2MzM4MzU5Y2U1NjlhNzUxMGQwIiwidXNlcl9pZCI6M30.-bNUjkaq5MDrkd8I7U3aGT-dpFhxZHDvhKKmshJisRc|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 7. Un profesor puede obtener las lista de materias a las que esta asignado
This endpoint makes an HTTP GET request to retrieve a list of professors from the API. The response will be in JSON format and will include an array of objects, each representing a professor with attributes such as id, name, code, description, credits, department, semester_number, is_active, professor, and prerequisites.

### Request Body

This request does not require a request body.

### Response Body

The response will be in JSON format and will include an array of objects, each representing a professor with the following attributes:

- id (integer): The unique identifier for the professor.
    
- name (string): The name of the professor.
    
- code (string): The code assigned to the professor.
    
- description (string): A brief description of the professor.
    
- credits (integer): The number of credits associated with the professor.
    
- department (string): The department to which the professor belongs.
    
- semester_number (integer): The semester number for the professor.
    
- is_active (boolean): Indicates whether the professor is active or not.
    
- professor (integer): The unique identifier for the professor.
    
- prerequisites (array): An array of prerequisite courses for the professor.
### Method: GET
>```
>http://localhost:8000/api/professor/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc2NDIzLCJpYXQiOjE3MzA0NzYxMjMsImp0aSI6Ijk3YmY0NzAzYWZiYzQ2MzM4MzU5Y2U1NjlhNzUxMGQwIiwidXNlcl9pZCI6M30.-bNUjkaq5MDrkd8I7U3aGT-dpFhxZHDvhKKmshJisRc|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 8. Un profesor puede ver la lista de estudiantes de cada una de sus materias
### Get Professor's Student List

This endpoint makes an HTTP GET request to retrieve the list of students associated with the professor with ID 4.

#### Request Body

This request does not require a request body.

#### Response

- Status: 200
    
- Content-Type: application/json
    
- \[\]
### Method: GET
>```
>http://localhost:8000/api/professor/4/student_list/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc2NDIzLCJpYXQiOjE3MzA0NzYxMjMsImp0aSI6Ijk3YmY0NzAzYWZiYzQ2MzM4MzU5Y2U1NjlhNzUxMGQwIiwidXNlcl9pZCI6M30.-bNUjkaq5MDrkd8I7U3aGT-dpFhxZHDvhKKmshJisRc|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 9. Un profesor finaliza la materia (califica cada estudiante)
This API endpoint allows the user to grade students for a specific professor. The HTTP POST request should be made to [http://localhost:8000/api/professor/4/grade_students/](http://localhost:8000/api/professor/4/grade_students/). The request body should be in raw format and should include an array of grades, where each grade object contains the student_id and the grade.

### Request Body

- `grades` (array of objects) - An array of objects containing the `student_id` (string) and `grade` (number) for each student.
    

#### Example

``` json
{
    "grades": [
        {
            "student_id": "10010",
            "grade": 2.8
        }
    ]
}
### Response
The API returns a 404 status code with a JSON response. The response body may include a `detail` key with a corresponding message.
#### Example
```json
{
    "detail": ""
}

 ```
### Method: POST
>```
>http://localhost:8000/api/professor/4/grade_students/
>```
### Body (**raw**)

```json
{
    "grades": [
        {
            "student_id": "10010",
            "grade": 2.8
        }
    ]
}
```

### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc2ODI4LCJpYXQiOjE3MzA0NzQ5OTcsImp0aSI6IjUwZDFjZjJiODZlYzRhYjA4ZWFhZjIyN2RmYzJkYjQxIiwidXNlcl9pZCI6Mn0.NzyDmaz0QDIuskv63v5kork6hckgeuIwrsLfycnVe9E|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: 10. Un profesor puede obtener las calificaciones de los estudiantes en sus materias
### Get Professor's Student Grades

This endpoint retrieves the grades of a specific professor's students.

#### Request

- Method: GET
    
- URL: `http://localhost:8000/api/professor/4/student_grades/`
    

#### Response

- Status: 404
    
- Content-Type: application/json
    
- { "detail": ""}
### Method: GET
>```
>http://localhost:8000/api/professor/4/student_grades/
>```
### 🔑 Authentication bearer

|Param|value|Type|
|---|---|---|
|token|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDc3MzA4LCJpYXQiOjE3MzA0NzcwMDgsImp0aSI6IjUzZDAyNTFlNjkyYjRkNWI5ZGM4NDEyZTQ1YzU3MjJjIiwidXNlcl9pZCI6MX0.ITIMqs1tLZ_nijg9ERG-k-Poax7h3zZbbDRDw98L_d0|string|



⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃
