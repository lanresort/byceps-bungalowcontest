"""
byceps.services.bungalow_contest.dbmodels.jury
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....database import db
from ....typing import UserID
from ....util.instances import ReprBuilder

from ..transfer.models import ContestID

from .contest import DbContest


class DbJuryMembership(db.Model):
    """An appointment of a user as a jury member for a contest."""

    __tablename__ = 'bungalow_contest_jury_memberships'

    contest_id = db.Column(
        db.Uuid, db.ForeignKey('bungalow_contests.id'), primary_key=True
    )
    contest = db.relationship(DbContest, backref='jury_memberships')
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)

    def __init__(self, contest_id: ContestID, user_id: UserID) -> None:
        self.contest_id = contest_id
        self.user_id = user_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('contest', self.contest.party.title) \
            .add('user_id', self.user_id) \
            .build()
