"""
byceps.services.bungalow_contest.dbmodels.contestant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from byceps.database import db
from byceps.services.bungalow.dbmodels.occupancy import DbBungalowOccupancy
from byceps.services.bungalow_contest.models import ContestantID, ContestID
from byceps.util.instances import ReprBuilder

from .contest import DbContest


MAXIMUM_UPLOADED_IMAGES_PER_CONTESTANT = 5


class DbContestant(db.Model):
    """A bungalow and its occupancy which take part in a contest."""

    __tablename__ = 'bungalow_contest_contestants'

    id = db.Column(db.Uuid, primary_key=True)
    contest_id = db.Column(
        db.Uuid,
        db.ForeignKey('bungalow_contests.id'),
        index=True,
        nullable=False,
    )
    contest = db.relationship(DbContest, backref='contestants')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    bungalow_occupancy_id = db.Column(
        db.Uuid,
        db.ForeignKey('bungalow_occupancies.id'),
        unique=True,
        index=True,
        nullable=False,
    )
    bungalow_occupancy = db.relationship(DbBungalowOccupancy)
    description = db.Column(db.UnicodeText, nullable=False)

    def __init__(
        self,
        contestant_id: ContestantID,
        contest_id: ContestID,
        bungalow_occupancy_id: UUID,
        description: str,
    ) -> None:
        self.id = contestant_id
        self.contest_id = contest_id
        self.bungalow_occupancy_id = bungalow_occupancy_id
        self.description = description

    @property
    def image_limit_reached(self) -> bool:
        """Return `True` if the maximum number of images for this
        contestant has been uploaded.
        """
        return len(self.images) >= MAXIMUM_UPLOADED_IMAGES_PER_CONTESTANT

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('party', self.contest.party_id)
            .add('bungalow', self.bungalow_occupancy.bungalow.number)
            .build()
        )


class DbImage(db.Model):
    """A picture representing the contestant."""

    __tablename__ = 'bungalow_contest_images'

    id = db.Column(db.Uuid, primary_key=True)
    contestant_id = db.Column(
        db.Uuid,
        db.ForeignKey('bungalow_contest_contestants.id'),
        index=True,
        nullable=False,
    )
    contestant = db.relationship(DbContestant, backref='images')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    caption = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        image_id: UUID,
        contestant_id: ContestantID,
        *,
        caption: str | None = None,
    ) -> None:
        self.id = image_id
        self.contestant_id = contestant_id
        self.caption = caption

    @property
    def url_path(self) -> str:
        party_id = self.contestant.contest.party_id
        return f'/data/parties/{party_id}/bungalow-contest/{self.filename}'

    @property
    def filename(self) -> str:
        return f'{self.id}.jpg'
