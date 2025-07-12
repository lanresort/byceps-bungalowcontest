"""
byceps.services.bungalow_contest.bungalow_contest_aggregation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict

from .dbmodels.contest import DbContest
from .dbmodels.rating import DbAttribute, DbRating
from .models import AggregatedAttributeRating, AttributeID, ContestantID


def aggregate_ratings(
    contest: DbContest,
) -> dict[ContestantID, dict[AttributeID, AggregatedAttributeRating]]:
    attrs = contest.attributes
    return {
        contestant.id: _process_contestant_ratings(attrs, contestant.ratings)
        for contestant in contest.contestants
    }


def _process_contestant_ratings(
    attributes: list[DbAttribute],
    ratings: list[DbRating],
) -> dict[AttributeID, AggregatedAttributeRating]:
    aggregated_attr_ratings = {}

    values_by_attr_id = _calculate_averages(ratings)
    for attr in attributes:
        values = values_by_attr_id[attr.id]
        rating_count = len(values)
        average_value = sum(values) / rating_count if rating_count != 0 else 0.0

        aggregated_attr_ratings[attr.id] = AggregatedAttributeRating(
            average_value=average_value,
            rating_count=rating_count,
        )

    return aggregated_attr_ratings


def _calculate_averages(
    ratings: list[DbRating],
) -> dict[AttributeID, list[int]]:
    values_by_attr_id = defaultdict(list)

    for rating in ratings:
        values_by_attr_id[rating.attribute.id].append(rating.value)

    return values_by_attr_id
