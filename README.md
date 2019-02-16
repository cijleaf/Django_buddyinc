# SunShot - mysunbuddy Python Code Challenge

## Overview

MySunBuddy is a peer-to-peer platform to facilitate the purchase and selling of solar net metering credits.

## Setup Prerequisites
* [Ubuntu 14+](http://www.ubuntu.com) - I am using 14.04 LTS 
* [Python 3.4+](http://www.python.org)
* [Django 1.8.6](https://www.djangoproject.com)
* [Git](http://git-scm.com)
* [AngularJS](http://angularjs.org)
* [Bootstrap](http://getbootstrap.com)
* [PVWatts (Version 5)](https://developer.nrel.gov/docs/solar/pvwatts-v5/)
* [celery 3.1](https://github.com/celery/celery) the async task framework
* [flake8](https://gitlab.com/pycqa/flake8) - check codes meet PEP8 standard
* [pep257](https://github.com/GreenSteam/pep257) - check codes meet PEP257 standard
* [GDAL](http://www.gdal.org/)

## Get key for PVWatts
Please check [get key](https://developer.nrel.gov/docs/api-key/)
It use demo key for now

##Get key for google map
Please check [get api key](https://developers.google.com/maps/documentation/geocoding/get-api-key)
You can just login in google and click **GET A KEY** it will create project and enable API for you.
Currently it use empty string and it has limit to request without key but you can use your own key.


## Installation Instructions


### Configuration
please modify ```mysunbuddy/settings.py```,it has below configuration parameters.
I just list important configurations,others please check [Django Settings](https://docs.djangoproject.com/en/1.8/topics/settings)
* **DATABASES** the database configuration,


### Development
1. (_optional_) Create a virtual env: `virtualenv -p python3 .venv; source .venv/bin/activate`
2. Clone the repo.
3. Run: `pip install -r requirements_dev.txt`
4. Copy the settings: `cp mysunbuddy/secure_settings.py.example mysunbuddy/secure_settings.py`
5. Run: `python manage.py migrate`
6. Fill in any credentials you need in `mysunbuddy/secure_settings.py`.
7. Run python manage.py runserver.


### Deployment
1. Run: `eb init`
2. Run: `eb deploy`

### Useful eb comands
* Environments:
```
$ eb list
production  # http://www.mysunbuddy.com
staging     # http://staging.mysunbuddy.com
```
* Get environment variables
```
$ eb printenv staging
 Environment Variables:
     AWS_ACCESS_KEY_ID = *****
     ...
```
* Set environment variable
`eb setenv -e staging VAR=VALUE`

## Run match schedular

run command with seed data  ```python3 seed_script.py```, only need to run once since it will actually run match job inside script.
run command  ```python3 match_script.py```.


## Periodic Task
It is configured in **CELERYBEAT_SCHEDULE**  in ```mysunbuddy/settings.py```.

Default it will run match task every 60 seconds.

## Shape file search
when sign up please use **145 VT-100, West Dover, VT 05356, USA** as address.

## Documentation
    # you can check directly generated html documents in docs/html
    # check PEP8
    sudo pip3 install flake8
    flake8 --max-line-length=180  mysunbuddy
    flake8 --max-line-length=180  rest_api
    flake8 --max-line-length=180  *.py
    
    # check PEP 257
    sudo pip3 install pep257
    pep257 mysunbuddy
    pep257 rest_api 
    pep257 *.py 
    
    
## Limitations
* You must make sure you can connect with google map well since it will use google map api.

## References

* [PEP 8](http://www.python.org/dev/peps/pep-0008/)
* [PEP 257](https://www.python.org/dev/peps/pep-0257/)
* [PVWatts (Version 5)](http://developer.nrel.gov/docs/solar/pvwatts-v5/)

