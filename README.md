# Contents
- [File Formats](#Formats)
- [Local Development Server](#LocalDevServer)
- [AWS Setup](#AWS)
    - [One Instance](#AWSOneInstance)
        - [AMI Setup](#AMIOneInstance)
        - [Flask Setup](#FlaskOneInstance)
        - [Neo4j Setup](#Neo4jOneInstance)
    - [Separate Instances](#AWSSepInstances)
        - [Flask Setup](#FlaskSepInstances)
        - [Neo4j Setup](#Neo4jSepInstances)

# <a name="Formats">File Formats</a>

# <a name="LocalDevServer">Local Development Server</a>

To test the website locally:

1. Clone the repository.
2. Navigate to the ClinicalCodingWebsite top level directory.
3. Setup the virtual environment in `/env`:
    - Download virtualenv.
    - Run `virtualenv env` to create the virtual environment.
4. Install the required Python packages:
    - Navigate to `/env`.
    - Run `bin/pip -r requirements.txt` (or possibly `Scripts/pip.exe` depending on the system).
5. Navigate back to the ClinicalCodingWebsite top level directory.
6. Run `/env/bin/python run.py`.
7. Go to the URL shown in the console.

# <a name="AWS">AWS Setup</a>

## <a name="AWSOneInstance">One Instance</a>

Use these instructions to run both the Flask app and the No4j database on the same instance. For additional information see the [links](#Links) at the bottom of the page.

### <a name="AMIOneInstance">AMI Setup</a>

We will use an Amazon Linux instance as it comes with Java 7 and you can easily install Open JDK 8 (which is needed for Neo4j version 3.0.3.

##### AWS Security Group

The security group will govern which ports and IPs the instance can receive requests from. We want SSH access limited to our development machine(s) and HTTP access open to all. We may also want access to the Neo4j database browser. We therefore create a security group with the following inbound settings:

|---|---|---|---|
|HTTP|TCP|80|0.0.0.0/0|
|SSH|TCP|22|xxxx|
|Custom TCP Rule|TCP|7474|xxxx|

- `xxxx` is the IP address that you intend to access the server from.
    - If needed, SSH connections from additional IPs can be added by adding more inbound rules.
- Port 7474 does not need to be open, but this will allow you to access the Neo4j database browser.
- While Neo4j needs port 7687 open for bolt access, there is no need to open the port to inbound traffic as everything is on one machine.

##### EC2 Instance Spin Up

1. Create the instance with the above security group settings.
2. Save the key somewhere you won't forget and make it so that only you can R/W it (e.g. `chmod 700`)
    - If the access to the key is not restricted to only your local account, then Amazon will reject your access.
3. Launch the instance.
    - From the EC2 management console, locate the public DNS for your instance (something like `ec2-**-***-***-**.eu-west-1.compute.amazonaws.com`).
    - SSH into the server `ssh -i /path/to/key.pem <username>@<public_DNS>`.
        - The username is `ec2-user` for an Amazon Linux instance.
        - The public DNS can be found using the AWS EC2 management console.
    - The web address of the instance will be its public DNS.

##### Software Updates

Now that we've logged in, we need to update the software to enable the Flask app and Neo4j database to function. The code is written in Python 3.4.5, so a Python 3 install is required.

1. Update packages - `sudo yum update -y`.
2. Get the Apache web server - `sudo yum install httpd24`.
    - Test that it's working:
        - Start the Apache web server - `sudo service httpd start`.
        - Check it is working by navigating to the public DNS.
    - Configure it to start at each boot up - `sudo chkconfig httpd on`.
3. Install Git - `sudo yum install git`.
4. Install mod_wsgi - `sudo yum install mod24_wsgi-python34`.
5. Install RabbitMQ - `sudo yum install librabbitmq`.
6. Install Python 3 (3.4 to be exact) - `sudo yum install python34`.
7. Install pip for Python 3 as presently (25/07/2016) it isn't getting bundled when downloading Python 3.4.
    - Run - `curl https://bootstrap.pypa.io/get-pip.py | sudo python34`.
8. Install Python packages needed:
    - Flask - `sudo /usr/local/bin/pip3.4 install flask`.
    - Flask WTF - `sudo /usr/local/bin/pip3.4 install flask_wtf`.
    - Neo4j Bolt driver - `sudo /usr/local/bin/pip3.4 install neo4j-driver`.
    - Celery `sudo /usr/local/bin/pip3.4 install celery`.


### <a name="FlaskOneInstance">Flask Setup</a>

##### Directory Set Up

1. From the home directory of your ec2 instance (`/home/ec2-user`) clone the project `git clone <project-repo>`.
    - `<project-repo>` should be this project's repository (https://github.com/SimonCB765/ClinicalCodingWebsite.git).
2. Alter the `WTF_CSRF_SECRET_KEY` and `SECRET_KEY` settings in `/home/ec2-user/ClinicalCodingWebsite/webapp/__init__.py` to be truly secret values.
3. Alter the Flask configuration used to set it up for production rather tha development.
    - Modify `/home/ec2-user/ClinicalCodingWebsite/webapp/__init__.py` by changing the line `app.config.from_object('config.DevelopmentConfig')` to `app.config.from_object('config.ProductionConfigLocal')`.
4. Create a symlink to the created project directory from the Apache document root (/var/www/html by default).
    - Run `sudo ln -s ~/ClinicalCodingWebsite/ /var/www/html/ClinicalCodingWebsite`.  

##### Configure Apache

Next we need to create a configuration file for the app. Create a file `amazonaws.com.conf` in `/etc/httpd/conf.d/` with the following content:

```
# Enable the following of the symbolic link we set up from the Apache document root to the project directory.
<Directory /var/www/html>
    Options FollowSymLinks
</Directory>

# Use an alias to get Apache to map any requests starting with /static to our static directory before they can be handled by our Flask app.
Alias /static /var/www/html/ClinicalCodingWebsite/webapp/static
<Directory /var/www/html/ClinicalCodingWebsite/webapp/static>
    Require all granted
</Directory>

# Grant access to the WSGI file. Do this via a directory section with the file we want to grant access to inside the nested directory construct.
<Directory /var/www/html/ClinicalCodingWebsite/>
    <Files ClinicalCodingWebsite.wsgi>
        Require all granted
    </Files>
</Directory>

# Use the recommended daemon mode configuration to run the WSGI process.
# This directive takes an arbitrary name for the process. Use ClinicalCodingWebsite to stay consistent.
WSGIDaemonProcess ClinicalCodingWebsite

# Specify the process group. This should point to the same name selected for the WSGIDaemonProcess directive.
WSGIProcessGroup ClinicalCodingWebsite

# Finally, set the script alias so that Apache will pass requests for the root domain to the WSGI file.
WSGIScriptAlias / /var/www/html/ClinicalCodingWebsite/ClinicalCodingWebsite.wsgi
```

Next, we need to fix permissions so that the Apache service can access the needed files, since CentOS default behaviour is to look down a user's home directory very restrictively. The default access settings for the `/home/ec2-user` directory is to allow `rwx` for `ec2-user` and deny all access for anyone else. To get around this, start by adding the `apache` user to the `ec2-user` group by running `sudo usermod -a -G ec2-user apache`.

As `ec2-user` is the group owner of `/home/ec2-user`, we can enable execute permission for the `ec2-user` group for `/home/ec2-user`. As user `apache` has ben added to the `ec2-user` group, this will give the Apache service the access it needs. Run `chmod 710 /home/ec2-user`.

Finally, reload the configuration files with `sudo /etc/init.d/httpd reload`.

Navigate to the public DNS and you should see the Flask portion of the site up and running. Next we need to enable Neo4j.

### <a name="Neo4jOneInstance">Neo4j Setup</a>

##### Setup Neo4j on the Server

Neo4j setup is fairly straightforward, and requires you to only change a few parameters. 

1. Download the Linux tarball from https://neo4j.com/download/other-releases/.
2. Transfer the tarball to the server by running `scp -i /path/to/key.pem /path/to/tarball.tar.gz <username>@<public_DNS>:/home/ec2-user`.
3. Log in to the server.
4. Untar the tarball with `tar xvfz tarball.tar.gz`.
    - Rename the directory that results to `Neo4j` with `sudo mv tarball /home/ec2-user/Neo4j`.
    - Remove the tarball if desired.
5. Get the recommended version of the JDK (OpenJDK 8 for Neo4j 3.0.3). Run the following commands in the given order to install version 8 and remove version 7 (run them in this order to ensure that aws-apitools isn't accidentally removed with version 7):
    - `sudo yum install java-1.8.0-openjdk`.
    - `sudo yum remove java-1.7.0-openjdk`.

##### Configure Neo4j

First, we need to enable access to Bolt and HTTP from any IP. These settings will not override the AWS security group settings, so it is easiest to open Bolt and HTTP to everyone here and restrict inbound traffic using the AWS security group settings. In `/home/ec2-user/Neo4j/conf/neo4j.conf` find the following sections:

```
# Bolt connector
...
# To have Bolt accept non-local connections, uncomment this line
# dbms.connector.bolt.address=0.0.0.0:7687

# HTTP Connector
...
# To have HTTP accept non-local connections, uncomment this line
# dbms.connector.http.address=0.0.0.0:7474
```

and uncomment the lines `# dbms.connector.bolt.address=0.0.0.0:7687` and `# dbms.connector.http.address=0.0.0.0:7474`. You can also enable access to HTTPS from non-localhost requests.

Next, we need to set up the instance to allow a user to have the recommended minimum of 40,000 files open simultaneously (as detailed <a href="http://neo4j.com/docs/operations-manual/current/#linux-open-files">here</a>).

1. Edit `/etc/security/limits.conf` to contain the following lines (if you want to run as a user other than root, then change the first value on each line to a different username):
    - `root   soft    nofile  40000`.
    - `root   hard    nofile  40000`.
2. Edit `/etc/pam.d/su` by uncommenting or adding the following line:
    - `session    required   pam_limits.so`.
    
Finally, we need to set the Java heap size to at least one gigabyte (if the instance Neo4j is being run on can handle that). In `/home/ec2-user/Neo4j/conf/neo4j-wrapper.conf` find the following lines:

```
# Java Heap Size: by default the Java heap size is dynamically
# calculated based on available system resources.
# Uncomment these lines to set specific initial and maximum
# heap size in MB.
#dbms.memory.heap.initial_size=512
#dbms.memory.heap.max_size=512
```

and uncomment and change the last two lines from 512 to 1024.

##### Final Steps

Start the Neo4j server running by running `/home/ec2-user/Neo4j/bin/neo4j start`.

Navigate to `<public_DNS>:7474`, where `<public_DNS>` is the public DNS of the instance, to set up the desired username and passowrd for the database.

Finally, alter the class variables `DATABASE_PASSWORD = "XXX"` and `DATABASE_USERNAME = "YYY"` of the `Config` class in the Flask application configuration file (`/home/ec2-user/ClinicalCodingWebsite/config.py`) so that `XXX` is the password you set up for the Neo4j database and `YYY` is the username you set up.

## <a name="AWSSepInstances">Separate Instances</a>

Use these instructions to run the Flask app on one instance and the Neo4j database on another. For additional information see the [links](#Links) at the bottom of the page.

### <a name="FlaskSepInstances">Flask Setup</a>

To set up the Flask instance, follow the instructions in sections [AMI Setup](#AMIOneInstance) and [Flask Setup](#FlaskOneInstance). Two changes to these procedures are needed. First, in the third step of the Directory Setup in the [AMI Setup](#AMIOneInstance) section, the correct configuration for the two instance setup is `app.config.from_object('config.ProductionConfigRemote')`. Second, the Flask instance security group should be set up as below rather than as directed in the [AMI Setup](#AMIOneInstance) instructions.

#### AWS Security Group

The security group will govern which ports and IPs the instance can receive requests from. We want SSH access limited to our development machine(s) and HTTP access open to all. We therefore create a security group named `FlaskApp` with the following inbound settings:

|---|---|---|---|
|HTTP|TCP|80|0.0.0.0/0|
|SSH|TCP|22|xxxx|

- `xxxx` is the IP address that you intend to access the server from.
    - If needed, SSH connections from additional IPs can be added by adding more inbound rules.

### <a name="Neo4jSepInstances">Neo4j Setup</a>

The instructions for setting up the standalone Neo4j instance are largely similar to those in the [Neo4j Setup](#Neo4jOneInstance) section with a few alterations to handle the fact that inbound traffic is expected from th Flask instance.

#### AWS Security Group

The security group will govern the which ports and IPs the instance can receive requests from. We want SSH access limited to our development machine(s) and the Flask app instance. We also want bolt access open to only the Flask app instance, and may also want access to the Neo4j database browser. We therefore create a security group with the following inbound settings:

|---|---|---|---|
|SSH|TCP|22|xxxx|
|SSH|TCP|22|FlaskApp|
|Custom TCP Rule|TCP|7474|xxxx|
|Custom TCP Rule|TCP|7687|FlaskApp|

- `xxxx` is the IP address that you intend to access the server from.
    - If needed, SSH connections from additional IPs can be added by adding more inbound rules.
- FlaskApp is the security group setup for the Flask app instance.
    - This will allow you to access the Neo4j instance from the Flask app instance.
- Port 7474 does not need to be open, but this will allow you to access the Neo4j database browser.
- Port 7687 needs opening for access from the Flask app instance in order to submit bolt queries to the database.

##### EC2 Instance Spin Up

1. Create the instance with the above security group settings.
2. Save the key somewhere you won't forget (or reuse the one generated for the Flask instance) and make it so that only you can R/W it (e.g. `chmod 700`)
    - If the access to the key is not restricted to only your local account, then Amazon will reject your access.
3. Launch the instance.
    - From the EC2 management console, locate the public DNS for your instance (something like `ec2-**-***-***-**.eu-west-1.compute.amazonaws.com`).
    - SSH into the server `ssh -i /path/to/key.pem <username>@<public_DNS>`.
        - The username is `ec2-user` for an Amazon Linux instance.
        - The public DNS can be found using the AWS EC2 management console.
    - The web address of the instance will be its public DNS.

##### Setup Neo4j on the Server

Neo4j setup is fairly straightforward, and requires you to only change a few parameters. 

1. Download the Linux tarball from https://neo4j.com/download/other-releases/.
2. Transfer the tarball to the server by running `scp -i /path/to/key.pem /path/to/tarball.tar.gz <username>@<public_DNS>:/home/ec2-user`.
3. Log in to the server.
4. Untar the tarball with `tar xvfz tarball.tar.gz`.
    - Rename the directory that results to `Neo4j` with `sudo mv tarball /home/ec2-user/Neo4j`.
    - Remove the tarball if desired.
5. Get the recommended version of the JDK (OpenJDK 8 for Neo4j 3.0.3). Run the following commands in the given order to install version 8 and remove version 7 (run them in this order to ensure that aws-apitools isn't accidentally removed with version 7):
    - `sudo yum install java-1.8.0-openjdk`.
    - `sudo yum remove java-1.7.0-openjdk`.

##### Configure Neo4j

First, we need to enable access to Bolt and HTTP from any IP. These settings will not override the AWS security group settings, so it is easiest to open Bolt and HTTP to everyone here and restrict inbound traffic using the AWS security group settings. In `/home/ec2-user/Neo4j/conf/neo4j.conf` find the following sections:

```
# Bolt connector
...
# To have Bolt accept non-local connections, uncomment this line
# dbms.connector.bolt.address=0.0.0.0:7687

# HTTP Connector
...
# To have HTTP accept non-local connections, uncomment this line
# dbms.connector.http.address=0.0.0.0:7474
```

and uncomment the lines `# dbms.connector.bolt.address=0.0.0.0:7687` and `# dbms.connector.http.address=0.0.0.0:7474`. You can also enable access to HTTPS from non-localhost requests.

Next, we need to set up the instance to allow a user to have the recommended minimum of 40,000 files open simultaneously (as detailed <a href="http://neo4j.com/docs/operations-manual/current/#linux-open-files">here</a>).

1. Edit `/etc/security/limits.conf` to contain the following lines (if you want to run as a user other than root, then change the first value on each line to a different username):
    - `root   soft    nofile  40000`.
    - `root   hard    nofile  40000`.
2. Edit `/etc/pam.d/su` by uncommenting or adding the following line:
    - `session    required   pam_limits.so`.
    
Finally, we need to set the Java heap size to at least one gigabyte (if the instance Neo4j is being run on can handle that). In `/home/ec2-user/Neo4j/conf/neo4j-wrapper.conf` find the following lines:

```
# Java Heap Size: by default the Java heap size is dynamically
# calculated based on available system resources.
# Uncomment these lines to set specific initial and maximum
# heap size in MB.
#dbms.memory.heap.initial_size=512
#dbms.memory.heap.max_size=512
```

and uncomment and change the last two lines from 512 to 1024.

##### Final Steps

Start the Neo4j server running by running `sudo /home/ec2-user/Neo4j/bin/neo4j start`.

Navigate to `<public_DNS>:7474`, where `<public_DNS>` is the public DNS of the instance, to set up the desired username and passowrd for the database.

Finally, alter the class variables `DATABASE_PASSWORD = "XXX"` and `DATABASE_USERNAME = "YYY"` of the `Config` class in the Flask application configuration file (`/home/ec2-user/ClinicalCodingWebsite/config.py`) so that `XXX` is the password you set up for the Neo4j database and `YYY` is the username you set up.

# <a name="Links"></a>Links

## Apache and Amazon Linux AMI

- http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-LAMP.html

## Flask and EC2 Amazon Linux AMI

- https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-centos-7
- https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/modwsgi/

## Flask and EC2 Ubuntu

- http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
- http://www.datasciencebytes.com/bytes/2015/02/24/running-a-flask-app-on-aws-ec2/
- http://alex.nisnevich.com/blog/2014/10/01/setting_up_flask_on_ec2.html

## Neo4j and EC2

- https://dzone.com/articles/how-deploy-neo4j-instance