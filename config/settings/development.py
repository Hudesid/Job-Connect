from .base import * #noqa

ALLOWED_HOSTS = ['*']

DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS += ["debug_toolbar"] # noqa: F405

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware'] # noqa: F405

REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}) # noqa: F405