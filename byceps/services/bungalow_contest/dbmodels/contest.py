"""
byceps.services.bungalow_contest.dbmodels.contest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.bungalow_contest.models import Phase
from byceps.services.party.dbmodels import DbParty
from byceps.services.party.models import PartyID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid4


class DbContest(db.Model):
    """A bungalow contest."""

    __tablename__ = 'bungalow_contests'

    id = db.Column(db.Uuid, default=generate_uuid4, primary_key=True)
    party_id = db.Column(
        db.UnicodeText,
        db.ForeignKey('parties.id'),
        unique=True,
        index=True,
        nullable=False,
    )
    party = db.relationship(DbParty)
    _phase = db.Column('phase', db.UnicodeText, nullable=False)

    def __init__(self, party_id: PartyID) -> None:
        self.party_id = party_id
        self._phase = Phase.not_started.name

    @hybrid_property
    def phase(self) -> Phase:
        return Phase[self._phase]

    @phase.setter
    def phase(self, phase: Phase) -> None:
        self._phase = phase.name

    def __repr__(self) -> str:
        return ReprBuilder(self).add('party', self.party_id).build()
