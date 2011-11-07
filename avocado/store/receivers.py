def descriptor_pre_diff(sender, reference, instance, config, **kwargs):
    config['exclude'] = ('pk', 'reference', 'session', 'modified', 'created', 'timestamp')

def descriptor_pre_reset(sender, reference, instance, config, **kwargs):
    config['exclude'] = ('pk', 'reference', 'session')

def descriptor_pre_fork(sender, reference, instance, config, **kwargs):
    config['exclude'] = ('pk', 'reference', 'session', 'user')
    config['deep'] = False

def descriptor_post_fork(sender, reference, instance, **kwargs):
    instance.user = reference.user

def descriptor_pre_commit(sender, reference, instance, **kwargs):
    # if the instance being committed is the session object, update
    # the reference
    if instance.session:
        instance.reference = reference

def descriptor_post_commit(sender, reference, instance, **kwargs):
    # this looks odd, but in the case of the persistent session object,
    # `reference' must keep a reference to the instance it is mimicking
    if reference.session:
        reference.reference = instance
        reference.commit()


def report_pre_diff(sender, reference, instance, config, **kwargs):
    if not config.get('fields', None):
        config['fields'] = ('name', 'description', 'keywords', 'scope', 'perspective')
    config['deep'] = True

def report_pre_reset(sender, reference, instance, config, **kwargs):
    config['exclude'] = ('pk', 'reference', 'session')
    config['deep'] = True

def report_pre_fork(sender, reference, instance, config, **kwargs):
    # reference and report_set are the same things, due to the self reference..
    config['exclude'] = ('pk', 'reference', 'session', 'user', 'report_set')
    config['deep'] = True
