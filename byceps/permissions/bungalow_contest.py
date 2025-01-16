"""
byceps.permissions.bungalow_contest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'bungalow_contest',
    [
        ('create', lazy_gettext('Bungalow-Contests erstellen')),
        ('manage', lazy_gettext('Bungalow-Contests verwalten')),
        ('view', lazy_gettext('Bungalow-Contests anzeigen')),
    ],
)
