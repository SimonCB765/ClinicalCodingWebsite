"""Long running tasks to be managed by Celery."""

# Celery imports.
from .. import celeryInstance

# User imports.
from . import ConceptCollection


@celeryInstance.task(bind=True)
def code_extraction(self, codes, positiveTerms, negativeTerms, codeFormat):
    """Long running task to extract a list of codes.

    :param self:
    :type self:
    :param codes:
    :type codes:
    :param positiveTerms:
    :type positiveTerms:
    :param negativeTerms:
    :type negativeTerms:
    :param codeFormat:
    :type codeFormat:
    :return:
    :rtype:

    """

    return {"Status": "Done"}


@celeryInstance.task(bind=True)
def concept_update(self, codes, positiveTerms, negativeTerms, codeFormat):
    """Long running task to update the concept definition and code hierarchy viewer.

    :param self:
    :type self:
    :param codes:
    :type codes:
    :param positiveTerms:
    :type positiveTerms:
    :param negativeTerms:
    :type negativeTerms:
    :param codeFormat:
    :type codeFormat:
    :return:
    :rtype:

    """

    return {"Status": "Done"}

#    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
#    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
#    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
#    message = ''
#    total = random.randint(10, 50)
#    for i in range(total):
#        if not message or random.random() < 0.25:
#            message = '{0} {1} {2}...'.format(random.choice(verb),
#                                              random.choice(adjective),
#                                              random.choice(noun))
#        self.update_state(state='PROGRESS',
#                          meta={'current': i, 'total': total,
#                                'status': message})
#        time.sleep(1)
#    return {'current': i, 'total': total, 'status': 'Task completed!',
#            'result': x + y}
