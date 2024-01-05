"""
byceps.blueprints.admin.bungalow_contest.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from byceps.services.bungalow import bungalow_service
from byceps.services.bungalow_contest import (
    bungalow_contest_aggregation_service,
    bungalow_contest_service,
)
from byceps.services.bungalow_contest.dbmodels import (
    # Load models.
    jury,  # noqa: F401
    rating,  # noqa: F401
)
from byceps.services.bungalow_contest.models import Phase
from byceps.services.party import party_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)


ATTRIBUTE_TITLES = [
    'Aufwand',
    'Erscheinungsbild',
    'Kreativität',
    'Themenbezug',
]


blueprint = create_blueprint('bungalow_contest_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('bungalow_contest.view')
@templated
def view(party_id):
    """Show an overview of the bungalow contest for that party."""
    party = _get_party_or_404(party_id)

    contest = bungalow_contest_service.find_contest_by_party_id(party.id)

    if not contest:
        return {
            'party': party,
            'contest': contest,
        }

    juror_ids = {membership.user_id for membership in contest.jury_memberships}
    jurors = user_service.get_users(juror_ids, include_avatars=True)

    attributes_ordered = list(sorted(contest.attributes, key=lambda a: a.title))

    aggregated_ratings = bungalow_contest_aggregation_service.aggregate_ratings(
        contest
    )

    rating_users_total = bungalow_contest_service.get_rating_users_total(
        contest.id
    )

    return {
        'party': party,
        'contest': contest,
        'Phase': Phase,
        'jurors': jurors,
        'attributes_ordered': attributes_ordered,
        'aggregated_ratings': aggregated_ratings,
        'rating_users_total': rating_users_total,
    }


@blueprint.post('/for_party/<party_id>')
@permission_required('bungalow_contest.create')
def create(party_id):
    """Create a bungalow contest for the party."""
    party = _get_party_or_404(party_id)

    contest = bungalow_contest_service.find_contest_by_party_id(party.id)
    if contest is not None:
        flash_error('A contest already exists for this party.')
        return redirect_to('.view', party_id=party.id)

    bungalow_contest_service.create_contest(party.id, ATTRIBUTE_TITLES)

    flash_success('Der Bungalow-Contest für diese Party wurde angelegt.')

    return redirect_to('.view', party_id=party.id)


@blueprint.post('/<contest_id>/phase/<phase_name>')
@permission_required('bungalow_contest.manage')
@respond_no_content
def switch_to_phase(contest_id, phase_name):
    """Switch contest to given phase."""
    phase = Phase.__members__.get(phase_name)
    if phase is None:
        abort(404)

    bungalow_contest_service.switch_contest_to_phase(contest_id, phase)

    flash_success('Die Phase wurde geändert.')


# -------------------------------------------------------------------- #


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    has_bungalows = bungalow_service.has_brand_bungalows(party.brand_id)
    if not has_bungalows:
        abort(404)

    return party
