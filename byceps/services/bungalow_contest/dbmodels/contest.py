"""
byceps.services.bungalow_contest.dbmodels.contest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db, generate_uuid
from ....typing import PartyID
from ....util.instances import ReprBuilder

from ...party.dbmodels.party import DbParty

from ..transfer.models import Phase


class Contest(db.Model):
    """A bungalow contest."""
    __tablename__ = 'bungalow_contests'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), unique=True, index=True, nullable=False)
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
        assert phase is not None
        self._phase = phase.name

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('party', self.party_id) \
            .build()
