"""
byceps.services.bungalow_contest.aggregation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from typing import Dict, List

from .models.contest import Contest
from .models.rating import Attribute, Rating
from .transfer.models import (
    AttributeID,
    AggregatedAttributeRating,
    ContestantID,
)


def aggregate_ratings(
    contest: Contest,
) -> Dict[ContestantID, Dict[AttributeID, AggregatedAttributeRating]]:
    attrs = contest.attributes
    return {
        contestant.id: _process_contestant_ratings(attrs, contestant.ratings)
        for contestant in contest.contestants
    }


def _process_contestant_ratings(
    attributes: List[Attribute],
    ratings: List[Rating],
) -> Dict[AttributeID, AggregatedAttributeRating]:
    aggregated_attr_ratings = {}

    values_by_attr_id = _calculate_averages(ratings)
    for attr in attributes:
        values = values_by_attr_id[attr.id]
        rating_count = len(values)
        avg_value = sum(values) / rating_count if rating_count != 0 else 0.0

        aggregated_attr_ratings[attr.id] = AggregatedAttributeRating(
            avg_value, rating_count
        )

    return aggregated_attr_ratings


def _calculate_averages(ratings: List[Rating]) -> Dict[AttributeID, List[int]]:
    values_by_attr_id = defaultdict(list)

    for rating in ratings:
        values_by_attr_id[rating.attribute.id].append(rating.value)

    return values_by_attr_id
