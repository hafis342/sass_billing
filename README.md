# SubTrack

This project is a backend system for a multi-tenant SaaS subscription and billing engine. It allows SaaS providers (vendors) to define products and subscription plans, manage customer subscriptions, track usage for usage-based billing, and generate invoices automatically. The system is designed to simulate the core business logic required for running a subscription-based SaaS platform Built using Django and Django REST Framework

## ⚙️ Tech Stack

- **Python** / **Django REST Framework (DRF)**
- **PostgreSQL** (recommended)
- **Poetry** for dependency and environment management

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/hafis342/sass_billing.git
    cd SubTrack
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv env
    source env/bin/activate
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```


## Running Locally

1. Ensure your virtual environment is activated:
    ```sh
    source env/bin/activate
    ```

2. Apply migrations:
    ```sh
    python manage.py migrate
    ```

3. Run the development server:
    ```sh
    python manage.py runserver
    ```

4. Open your browser and navigate to `http://127.0.0.1:8000/`.

5. Run the command for creating platform admin:
    ```sh
    python manage.py create_admin
    ```

5. Run the command for creating user roles:
    ```sh
    python manage.py create_roles
    ```



Base URL `http://127.0.0.1:8000/`.

Swagger UI: `http://127.0.0.1:8000/swagger/`
