"""
byceps.services.bungalow_contest.bungalow_contest_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional
from uuid import UUID

from ...database import db
from ...typing import PartyID, UserID

from ..user.dbmodels.user import DbUser

from .dbmodels.contest import DbContest
from .dbmodels.contestant import DbContestant
from .dbmodels.jury import DbJuryMembership
from .dbmodels.rating import DbAttribute, DbRating
from .transfer.models import AttributeID, ContestantID, ContestID, Phase


# -------------------------------------------------------------------- #
# contest


def create_contest(party_id: PartyID, attribute_titles: set[str]) -> ContestID:
    """Create a contest for that party."""
    contest = DbContest(party_id)
    db.session.add(contest)

    for title in attribute_titles:
        attribute = DbAttribute(contest, title)
        db.session.add(attribute)

    db.session.commit()

    return contest.id


def find_contest(contest_id: ContestID) -> Optional[DbContest]:
    """Return the contest, if it exists."""
    return db.session.query(DbContest).get(contest_id)


def find_contest_by_party_id(party_id: PartyID) -> Optional[DbContest]:
    """Return the contest for that party, if it exists."""
    return DbContest.query \
        .filter_by(party_id=party_id) \
        .one_or_none()


def switch_contest_to_phase(contest_id: ContestID, phase: Phase) -> None:
    """Switch the contest to that phase."""
    contest = find_contest(contest_id)
    if contest is None:
        raise ValueError('Unknown contest ID')

    contest.phase = phase
    db.session.commit()


# -------------------------------------------------------------------- #
# contestant


def find_contestant(
    party_id: PartyID, contestant_id: ContestantID
) -> Optional[DbContestant]:
    """Return the contestant with that ID, if it exists.

    The party ID is checked as an additional measure so that a
    contestant is not returned if it doesn't belong to the current
    site's party.
    """
    return DbContestant.query \
        .join(DbContest) \
        .filter(DbContest.party_id == party_id) \
        .filter(DbContestant.id == contestant_id) \
        .one_or_none()


def find_contestant_for_bungalow(
    bungalow_occupancy_id: UUID,
) -> Optional[DbContestant]:
    """Return the registration of the bungalow for the contest, if it exists."""
    return DbContestant.query \
        .filter_by(bungalow_occupancy_id=bungalow_occupancy_id) \
        .one_or_none()


def is_bungalow_contestant(bungalow_occupancy_id: UUID) -> bool:
    """Return `True` if the bungalow is registered for the contest."""
    count = DbContestant.query \
        .filter_by(bungalow_occupancy_id=bungalow_occupancy_id) \
        .count()
    return count > 0


def register_contestant(
    contest_id: ContestID, bungalow_occupancy_id: UUID, description: str
) -> DbContestant:
    """Register a bungalow as a contestant for a party."""
    contestant = DbContestant(contest_id, bungalow_occupancy_id, description)

    db.session.add(contestant)
    db.session.commit()

    return contestant


# -------------------------------------------------------------------- #
# jury


def appoint_juror(user_id: UserID, contest_id: ContestID) -> None:
    """Appoint the user as a juror for that contest."""
    jury_membership = DbJuryMembership(contest_id, user_id)

    db.session.add(jury_membership)
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
    rating = DbRating.query \
        .filter_by(contestant_id=contestant_id) \
        .filter_by(attribute_id=attribute_id) \
        .filter_by(creator_id=creator_id) \
        .one_or_none()

    if rating:
        rating.value = value
    else:
        rating = DbRating(contestant_id, attribute_id, creator_id, value)
        db.session.add(rating)

    db.session.commit()


def get_ratings_by_user(
    user_id: UserID, contestant_id: ContestantID
) -> dict[UUID, DbRating]:
    """Return the user's ratings for that contestant, indexed by attribute."""
    ratings = DbRating.query \
        .filter_by(contestant_id=contestant_id) \
        .filter_by(creator_id=user_id) \
        .all()

    return {r.attribute_id: r for r in ratings}


def get_rating_users_total(contest_id: ContestID) -> int:
    """Return the number of unique users that have rated bungalows in
    this contest.
    """
    return DbUser.query \
        .join(DbRating) \
        .join(DbContestant) \
        .filter(DbContestant.contest_id == contest_id) \
        .distinct() \
        .count()
