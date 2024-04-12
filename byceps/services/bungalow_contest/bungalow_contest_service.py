"""
byceps.services.bungalow_contest.bungalow_contest_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID

from .dbmodels.contest import DbContest
from .dbmodels.contestant import DbContestant
from .dbmodels.jury import DbJuryMembership
from .dbmodels.rating import DbAttribute, DbRating
from .models import AttributeID, ContestantID, ContestID, Phase


# -------------------------------------------------------------------- #
# contest


def create_contest(party_id: PartyID, attribute_titles: set[str]) -> ContestID:
    """Create a contest for that party."""
    db_contest = DbContest(party_id)
    db.session.add(db_contest)

    for title in attribute_titles:
        db_attribute = DbAttribute(db_contest, title)
        db.session.add(db_attribute)

    db.session.commit()

    return db_contest.id


def find_contest(contest_id: ContestID) -> DbContest | None:
    """Return the contest, if it exists."""
    return db.session.get(DbContest, contest_id)


def find_contest_by_party_id(party_id: PartyID) -> DbContest | None:
    """Return the contest for that party, if it exists."""
    return db.session.execute(
        select(DbContest).filter_by(party_id=party_id)
    ).scalar_one_or_none()


def switch_contest_to_phase(contest_id: ContestID, phase: Phase) -> None:
    """Switch the contest to that phase."""
    db_contest = find_contest(contest_id)
    if db_contest is None:
        raise ValueError('Unknown contest ID')

    db_contest.phase = phase
    db.session.commit()


# -------------------------------------------------------------------- #
# contestant


def find_contestant(
    party_id: PartyID, contestant_id: ContestantID
) -> DbContestant | None:
    """Return the contestant with that ID, if it exists.

    The party ID is checked as an additional measure so that a
    contestant is not returned if it doesn't belong to the current
    site's party.
    """
    return db.session.execute(
        select(DbContestant)
        .join(DbContest)
        .filter(DbContest.party_id == party_id)
        .filter(DbContestant.id == contestant_id)
    ).scalar_one_or_none()


def find_contestant_for_bungalow(
    bungalow_occupancy_id: UUID,
) -> DbContestant | None:
    """Return the registration of the bungalow for the contest, if it exists."""
    return db.session.execute(
        select(DbContestant).filter_by(
            bungalow_occupancy_id=bungalow_occupancy_id
        )
    ).scalar_one_or_none()


def is_bungalow_contestant(bungalow_occupancy_id: UUID) -> bool:
    """Return `True` if the bungalow is registered for the contest."""
    return (
        db.session.scalar(
            select(
                select(DbContestant.id)
                .filter_by(bungalow_occupancy_id=bungalow_occupancy_id)
                .exists()
            )
        )
        or False
    )


def register_contestant(
    contest_id: ContestID, bungalow_occupancy_id: UUID, description: str
) -> DbContestant:
    """Register a bungalow as a contestant for a party."""
    db_contestant = DbContestant(contest_id, bungalow_occupancy_id, description)

    db.session.add(db_contestant)
    db.session.commit()

    return db_contestant


# -------------------------------------------------------------------- #
# jury


def appoint_juror(user_id: UserID, contest_id: ContestID) -> None:
    """Appoint the user as a juror for that contest."""
    db_jury_membership = DbJuryMembership(contest_id, user_id)

    db.session.add(db_jury_membership)
    db.session.commit()


# -------------------------------------------------------------------- #
# rating


def rate(
    contestant_id: ContestantID,
    attribute_id: AttributeID,
    creator_id: UserID,
    value: int,
) -> None:
    """Create or update a user's rating for a bungalow's attribute."""
    db_rating = db.session.execute(
        select(DbRating)
        .filter_by(contestant_id=contestant_id)
        .filter_by(attribute_id=attribute_id)
        .filter_by(creator_id=creator_id)
    ).scalar_one_or_none()

    if db_rating:
        db_rating.value = value
    else:
        db_rating = DbRating(contestant_id, attribute_id, creator_id, value)
        db.session.add(db_rating)

    db.session.commit()


def get_ratings_by_user(
    user_id: UserID, contestant_id: ContestantID
) -> dict[UUID, DbRating]:
    """Return the user's ratings for that contestant, indexed by attribute."""
    db_ratings = db.session.scalars(
        select(DbRating)
        .filter_by(contestant_id=contestant_id)
        .filter_by(creator_id=user_id)
    ).all()

    return {db_rating.attribute_id: db_rating for db_rating in db_ratings}


def get_rating_users_total(contest_id: ContestID) -> int:
    """Return the number of unique users that have rated bungalows in
    this contest.
    """
    return db.session.scalar(
        select(db.func.count(DbUser.id))
        .join(DbRating)
        .join(DbContestant)
        .filter(DbContestant.contest_id == contest_id)
        .distinct()
    ) or 0
