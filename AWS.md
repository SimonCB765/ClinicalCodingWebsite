# Introduction

For more detailed information see the [links](#Links) at the bottom of the page.

# EC2 Instance Spin Up

1. Launch an EC2 instance (assumed to be Ubuntu here).
    * Save the key generated during this process somewhere you won't forget.
    * Make the key R/W only by you (e.g. chmod 700)
2. From the EC2 management console, locate the public DNS for your instance (something like ec2-\*\*-\*\*\*-\*\*\*-\*\*.eu-west-1.compute.amazonaws.com).
3. SSH into the server (ssh -i /path/to/key.pem \<username\>@\<address\>
    * The username is ubuntu for an ubuntu instance.
    * The address is the public DNS of the instance.

# Download Required Packages

1. Update package list - `sudo apt-get update`.
2. Install Git - `sudo apt-get install git`.
3. Get the Apache web server - `sudo apt-get install apache2`.
4. Install Python-related content.
    1. For Python 2.x.
        1. Install mod_wsgi `sudo apt-get install libapache2-mod-wsgi`.
        2. Install pip `sudo apt-get install python-pip`.
        3. Install Flask `sudo pip install flask`.
    2. For Python 3.x.
        1. Install mod_wsgi `sudo apt-get install libapache2-mod-wsgi-py3`.
        2. Install pip `sudo apt-get install python3-pip`.
        3. Install Flask `sudo pip3 install flask`.

# Directory Set Up

1. From the home directory of your ec2 instance (/home/ubuntu for Ubuntu instances) clone the project `git clone <project-repo>`.
2. Create a symlink to the created project directory from the site-root defined in apache's configuration (/var/www/html by default).
3. Navigate to the project directory - `cd ~/ClinicalCodingWebsite`.

# Create the .wsgi File

Next we need to create a .wsgi file to load the app. In a file named `ClinicalCodingWebsite.wsgi` place the following:

```python
import sys
sys.path.insert(0, "/var/www/html/ClinicalCodingWebsite")

from webapp import app as application
```

# Create an Apache Configuration File

Next we need to create a configuration file for the app.

```
<VirtualHost *:80>
    ServerName http://ec2-**-***-***-**.eu-west-1.compute.amazonaws.com/
    WSGIDaemonProcess ClinicalCodingWebsite threads=5
    WSGIScriptAlias / /var/www/html/ClinicalCodingWebsite/ClinicalCodingWebsite.wsgi
    <Directory /var/www/html/ClinicalCodingWebsite/>
        WSGIProcessGroup ClinicalCodingWebsite
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```

Save this file as, for example, `amazonaws.com.conf` in `/etc/apache2/sites-available/`. 

# Start the Application

Finally we need to enable the configured application, and start the server up.

1. Enable the configuration - `sudo a2ensite amazonaws.com`.
2. Disable the default configuration - `sudo a2dissite 000-default`.
3. Reload - `sudo /etc/init.d/apache2 reload`.
4. Restart - `sudo apachectl restart`.

Now navigate to http://ec2-*\*-\*\*\*-\*\*\*-\*\*.eu-west-1.compute.amazonaws.com/concept_discovery/ and you should see you the site.

# <a name="Links"></a>Links

* http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
* http://www.datasciencebytes.com/bytes/2015/02/24/running-a-flask-app-on-aws-ec2/
* http://alex.nisnevich.com/blog/2014/10/01/setting_up_flask_on_ec2.html