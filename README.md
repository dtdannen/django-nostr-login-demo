# django-nostr-login-demo
This is a simple demo of how to use Nostr extensions for authentication, using Django's built-in User models.

Note: Please submit a PR if you can improve this!

# Install

Get the repo:

```commandline
git clone https://github.com/dtdannen/django-nostr-login-demo.git
cd django-nostr-login-demo
```

Set up your virtualenv

```commandline
python3 -m venv venv
```

Install requirements

```commandline
pip install -r requirements.txt
```

# Run

The first time you run it, you'll need to migrate the database:

```commandline
python manage.py migrate
```



```commandline
python manage.py runserver
```

