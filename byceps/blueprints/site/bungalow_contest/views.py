"""
byceps.blueprints.site.bungalow_contest.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, current_app, g, request

from ....database import db
from ....services.bungalow import bungalow_service
from ....services.bungalow.occupancy import bungalow_occupancy_service
from ....services.bungalow_contest.dbmodels.contestant import (
    DbContestant,
    MAXIMUM_UPLOADED_IMAGES_PER_CONTESTANT,
)
from ....services.bungalow_contest.dbmodels import jury  # Load models.
from ....services.bungalow_contest.dbmodels.rating import DbAttribute
from ....services.bungalow_contest import (
    bungalow_contest_image_service,
    bungalow_contest_service,
)
from ....services.bungalow_contest.transfer.models import Phase
from ....services.user import user_service
from ....services.user.transfer.models import User
from ....signals import bungalow_contest as bungalow_contest_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.image.models import Dimensions, ImageType
from ....util.framework.templating import templated
from ....util.views import login_required, redirect_to, respond_no_content

from .forms import ContestantUpdateForm, ImageCreateForm


ALLOWED_IMAGE_TYPES = frozenset(
    [
        ImageType.jpeg,
    ]
)


MAXIMUM_DIMENSIONS = Dimensions(1280, 1024)


blueprint = create_blueprint('bungalow_contest', __name__)


@blueprint.get('/')
@templated
def index():
    """The entry page for the contest, showing information based on the
    state of the contest, the current user's bungalow and its state as
    a contestant.
    """
    contest = _get_contest_or_404()

    inhabited_bungalow = bungalow_service.find_bungalow_inhabited_by_user(
        g.user.id, g.party_id
    )

    if inhabited_bungalow:
        inhabited_bungalow_manager_id = (
            inhabited_bungalow.occupancy.occupied_by_id
        )
        inhabited_bungalow_manager = user_service.find_user(
            inhabited_bungalow_manager_id
        )
    else:
        inhabited_bungalow_manager = None

    occupancy = bungalow_occupancy_service.find_occupancy_managed_by_user(
        g.party_id, g.user.id
    )

    contestant = None
    if contest and occupancy:
        contestant = bungalow_contest_service.find_contestant_for_bungalow(
            occupancy.id
        )

    return {
        'contest': contest,
        'Phase': Phase,
        'inhabited_bungalow': inhabited_bungalow,
        'inhabited_bungalow_manager': inhabited_bungalow_manager,
        'occupancy': occupancy,
        'contestant': contestant,
    }


@blueprint.get('/contestants/<uuid:id>')
@templated
def view_contestant(id):
    """View a constestant's presentation."""
    contestant = _get_contestant_or_404(id)

    occupants = _get_occupants(contestant)

    return {
        'contestant': contestant,
        'occupants': occupants,
    }


@login_required
@blueprint.post('/register')
def register():
    """Register an occupied bungalow as a contestant."""
    contest = _get_contest_or_404()

    occupancy = bungalow_occupancy_service.find_occupancy_managed_by_user(
        g.party_id, g.user.id
    )

    if (occupancy is None) or not occupancy.is_managed_by(g.user.id):
        flash_error(
            'Nur der/die Bungalowverwalter/in '
            'kann einen Bungalow zum Wettbewerb anmelden.'
        )
        return redirect_to('.index')

    if bungalow_contest_service.is_bungalow_contestant(occupancy.id):
        flash_error(
            f'Bungalow {occupancy.bungalow.number} '
            'ist bereits zum Wettbewerb angemeldet.'
        )
        return redirect_to('.index')

    description = ''

    bungalow_contest_service.register_contestant(
        contest.id, occupancy.id, description
    )

    flash_success(
        f'Du hast Bungalow {occupancy.bungalow.number} '
        'für den Wettbewerb angemeldet.'
    )
    bungalow_contest_signals.contestant_registered.send(
        None, contest=contest, occupancy=occupancy
    )

    return redirect_to('.index')


@blueprint.get('/contestants/<uuid:id>/update')
@login_required
@templated
def update_contestant_form(id, *, erroneous_form=None):
    """Update the description of the contestant."""
    contestant = _get_contestant_or_404(id)

    form = (
        erroneous_form
        if erroneous_form
        else ContestantUpdateForm(obj=contestant)
    )

    return {
        'contestant': contestant,
        'form': form,
    }


@blueprint.post('/contestants/<uuid:id>')
@login_required
def update_contestant(id):
    """Update the contestant."""
    contestant = _get_contestant_or_404(id)

    form = ContestantUpdateForm(request.form)

    if not form.validate():
        return update_contestant_form(id, erroneous_form=form)

    contestant.description = form.description.data.strip()
    db.session.commit()

    flash_success('Die Beschreibung wurde aktualisiert.')
    bungalow_contest_signals.contestant_updated.send(
        None, contestant=contestant
    )

    return redirect_to('.view_contestant', id=contestant.id)


@blueprint.get('/contestants/<uuid:id>/images/update')
@login_required
@templated
def update_contestant_images_form(id, *, erroneous_form=None):
    """Update the images of the contestant."""
    contestant = _get_contestant_or_404(id)

    form = erroneous_form if erroneous_form else ImageCreateForm()

    return {
        'contestant': contestant,
        'form': form,
        'MAXIMUM_UPLOADED_IMAGES_PER_CONTESTANT': MAXIMUM_UPLOADED_IMAGES_PER_CONTESTANT,
    }


@blueprint.post('/contestants/<uuid:id>/images')
@login_required
def create_contestant_image(id):
    """Upload a picture to present the contestant."""
    contestant = _get_contestant_or_404(id)

    if contestant.image_limit_reached:
        abort(409, 'Maximum number of allowed images reached.')

    form = ImageCreateForm(request.form)

    if not form.validate():
        return update_contestant_form(id, erroneous_form=form)

    image = request.files.get('image')
    if not image or not image.filename:
        abort(400, 'No file to upload has been specified.')

    caption = form.caption.data.strip()

    try:
        bungalow_contest_image_service.upload(
            contestant,
            image.stream,
            ALLOWED_IMAGE_TYPES,
            MAXIMUM_DIMENSIONS,
            caption=caption,
        )
    except bungalow_contest_image_service.ImageTypeProhibited as e:
        abort(400, str(e))
    except FileExistsError:
        abort(409, 'File already exists, not overwriting.')

    flash_success('Das Bild wurde eingefügt.', icon='upload')
    bungalow_contest_signals.contestant_image_created.send(
        None, contestant=contestant
    )

    return redirect_to('.update_contestant_images_form', id=contestant.id)


@blueprint.get('/contestants')
@templated
def contestants():
    """List constestants."""
    contest = _get_contest_or_404()

    user_ratings_by_contestant = {}
    if g.user.authenticated:
        for contestant in contest.contestants:
            user_ratings_by_contestant[
                contestant.id
            ] = bungalow_contest_service.get_ratings_by_user(
                g.user.id, contestant.id
            )

    return {
        'contest': contest,
        'Phase': Phase,
        'user_ratings_by_contestant': user_ratings_by_contestant,
    }


@blueprint.put('/ratings')
@login_required
@respond_no_content
def rate():
    """Create/update a user's rating for a bungalow's attribute."""
    json_data = request.get_json()

    if json_data is None:
        abort(400)

    contestant_id = json_data.get('contestant_id')
    if not contestant_id:
        abort(400, 'Missing contestant ID.')

    contestant = bungalow_contest_service.find_contestant(
        g.party_id, contestant_id
    )
    if contestant is None:
        abort(400, 'Unknown contestant ID.')

    attribute_id = json_data.get('attribute_id')
    if not attribute_id:
        abort(400, 'Missing attribute ID.')

    creator = g.user

    value = json_data.get('value')
    if not value:
        abort(400, 'Missing value.')

    contestant = db.session.query(DbContestant).get(contestant_id)
    if not contestant:
        abort(400, 'Unknown contestant ID.')

    attribute = db.session.query(DbAttribute).get(attribute_id)
    if not attribute:
        abort(400, 'Unknown attribute ID.')

    bungalow_contest_service.rate(
        contestant.id, attribute.id, creator.id, value
    )


def _get_contest_or_404():
    contest = bungalow_contest_service.find_contest_by_party_id(g.party_id)

    if contest is None:
        abort(404)

    return contest


def _get_contestant_or_404(contestant_id):
    contestant = bungalow_contest_service.find_contestant(
        g.party_id, contestant_id
    )

    if contestant is None:
        abort(404)

    return contestant


def _get_occupants(contestant) -> set[User]:
    area_id = contestant.bungalow_occupancy.bungalow.seating_area.id

    seats_and_user_ids = bungalow_service.get_seats_and_user_ids_for_areas(
        {area_id}
    )
    user_ids = {user_id for seat, user_id in seats_and_user_ids if user_id}

    return user_service.get_users(user_ids)
