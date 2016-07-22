TODO
    Production configuration will need changing if we run the Neo4j off the same server
        bt still note that you can run it off another server using the public DNS

Background database queries
    RabbitMQ
        sudo apt-get update
        sudo apt-get install rabbitmq-server
        start it in the background
            sudo rabbitmq-server -detached
    Celerey
        sudo pip install celery
    Windows manual start up
        env\Scripts\celery.exe worker -A webapp.celeryInstance



Concept definition notes
    codes included will have all alphanumerc charcters removed, except for a final % if one is present
    the uploaded file format is taken from the extension (.txt, .csv or .tsv for flat file and .json for JSON) (case insensitive)
    Json shuld really have lists for the terms and codes (e.g. "Terms": [..]) but will accept dicts (e.g. "Terms": {"term1": .., "Term2": ..})
        it will just take the keys as the list of terms


Notes
    Need to switch between development and production config in webapp init
    jQuery 3.1.0 in use


Security groups
    set the neo4j access so that access is limited to specific IPs development will occur from and the security group that the webapp server is in
        if you set it to just the webapp group, then you can only access the neo4j server from instances with the webapp security group
        you won't be able to access it from any development machines


Additional module installs needed on webapp server
    sudo pip3 install flask_wtf
    sudo pip3 install neo4j-driver

Accessing neo4j server from web app
    Can do it using the public dns of the neo4j server, e.g. ec2....:port
        http://stackoverflow.com/a/12482753
        http://serverfault.com/a/695351


neo4j running on ec2
    Set up is for Neo4j 3.0.3
	choose amazon linux as it comes with java (7) and you can install 8 easily
	username is ec2-user
	The security group needs
		have SSH (port 22) open (preferably to a set IP)
            for uploading stuff via scp and sshing in
		have ports 7474 and 7687 open to allow whatever IP addresses you want to access them
            7474 for accessing the browser interface if you want
            7687 for the bolt interface

	have to get neo4j from the tarball...
	transfer it with
		scp -i MRCWebapp.pem neo4j-community-3.0.3-unix.tar.gz ec2-user@ec2-52-209-72-113.eu-west-1.compute.amazonaws.com:/home/ec2-user
	untar it
		tar xvfz neo4j-community-1.6.M01-unix.tar.gz.tar.gz
	Rename the folder to Neo4j
		sudo mv neo4j-community-1.6.M01 ~/Neo4j

	Enable access to bolt and http from any IP
		in ~/Neo4j/conf/neo4j.conf
			# Bolt connector
			...
			# To have Bolt accept non-local connections, uncomment this line
			# dbms.connector.bolt.address=0.0.0.0:7687
            
            # HTTP Connector
            ...
            # To have HTTP accept non-local connections, uncomment this line
            # dbms.connector.http.address=0.0.0.0:7474
		uncomment the last lines (dbms connector ones)

	Get the correct version of JAva (7 is the default and we need 8 as of neo4j 3.0.3)
		sudo yum install java-1.8.0-openjdk
		sudo yum remove java-1.7.0-openjdk
		in this order to be safe so that it doesn't remove the aws-apitools when you remove 7

	Set it up so that you can open the recommended minimum of 40000 simultaneous files
		http://neo4j.com/docs/operations-manual/current/#linux-open-files
		if you want to run as a user other than root, then change the first entries on the line to the username
		Edit /etc/security/limits.conf and add these two lines (need to sudo as protected):
			root   soft    nofile  40000
			root   hard    nofile  40000
		Edit /etc/pam.d/su and uncomment or add the following line (need to sudo as protected):
			session    required   pam_limits.so
    
    In conf/neo4j-wrapper.conf set the java heap size to at least 1GB if you can (free t2.micro instances can't)
        Uncomment the last two lines
        
        # Java Heap Size: by default the Java heap size is dynamically
        # calculated based on available system resources.
        # Uncomment these lines to set specific initial and maximum
        # heap size in MB.
        #dbms.memory.heap.initial_size=512
        #dbms.memory.heap.max_size=512

	start the neo4j server
		from the neo4j server folder do sudo ~/Neo4j/bin/neo4j start
       
    got to http://ec2-52-209-72-113.eu-west-1.compute.amazonaws.com:7474/ (or whatever the public dns is)
        set up the new password

    https://dzone.com/articles/how-deploy-neo4j-instance