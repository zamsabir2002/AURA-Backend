## Steps to run backend

### Step: 1: Create Virtual Environment:

### Linux

If pip is not in your system

```bash
$ sudo apt-get install python-pip
```

Then install virtualenv

```bash
$ pip install virtualenv
```

Now check your installation

```
$ virtualenv --version
```

Create a virtual environment now,

```
$ virtualenv venv
```

After this command, a folder named `venv` will be created. You can name anything to it.
Now activate it, using command

```
$ source venv/bin/activate
```

### Windows

If python is installed in your system, then pip comes in handy.

Install virtualenv

```
pip install virtualenv
```

Now in which ever directory you are, this line below will create a virtualenv there

```
python -m venv venv
```

And here also you can name it anything.

Now if you are same directory then type,

```
venv\Scripts\activate
```

### If this shows a powershell security error do the following else skip

### Bypass powershell security error: (Run any one)

#### For current process:

    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

#### For current user:

    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser

## Step 2: Installing Dependencies:

1.  Make sure you are in AURA-BACKEND folder with the venv activated
2.  Run the following command:

        pip install -r requirements.txt

3.  After installation is done move to Step 3

## Step 3: Running the Backend server:

## On Linux

```
sudo `which python` manage.py runserver
```

## On Windows

```
python manage.py runserver
```

## Additional Requirements:

- To run RabbitMQ server run the following docker command (Make sure you have docker installed and running)

```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management
```
