The local, one instance and two instance setups are missing the rabbitmq and celery start up

Background database queries
    RabbitMQ
        start it in the background
            sudo rabbitmq-server -detached
    Windows manual start up
        env\Scripts\celery.exe worker -A webapp.celeryInstance



Concept definition notes
    Json shuld really have lists for the terms and codes (e.g. "Terms": [..]) but will accept dicts (e.g. "Terms": {"term1": .., "Term2": ..})
        it will just take the keys as the list of terms


Notes
    jQuery 3.1.0 in use