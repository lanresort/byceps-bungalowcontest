"""
byceps.blueprints.admin.bungalow_contest.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


BungalowContestPermission = create_permission_enum(
    'bungalow_contest',
    [
        'create',
        'manage',
        'view',
    ],
)
