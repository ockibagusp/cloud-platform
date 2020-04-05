# cloud-platform
IoT Cloud-Platfrom Web API

# Python Dependencies

- This application require python packages written on `/requirements.txt`.
- Listing:
```shell
pymongo>=3.3.1
Django>=1.11.23
pymongo>=3.3.1
mongoengine>=0.10.6
djangorestframework_jwt>=1.8.0
django_rest_framework_mongoengine>=3.3.1
PyJWT>=1.4.2
djangorestframework>=3.9.1
django-cors-headers>=1.3.1
paho-mqtt>=1.3.1
```

# Preparation
## Cloud-Platform (WebService)

1. Clone repository from Github

```bash
$ git clone https://github.com/OckiFals/cloud-platform.git
```

## Web-Console (Single-Page Application)

1. Clone repository from Github

```bash
$ git clone https://github.com/OckiFals/web-console.git
```

2. Change directory to cloned repo

```bash
$ cd /your-path/web-console
```

3. Install dependencies

```bash
$ npm install
```

4. Build

```bash
$ npm run prod-build
```

Build location: `/your-path/web-console/dist`
