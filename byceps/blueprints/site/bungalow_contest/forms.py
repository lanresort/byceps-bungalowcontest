"""
byceps.blueprints.site.bungalow_contest.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import FileField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional

from byceps.util.l10n import LocalizedForm


class ContestantUpdateForm(LocalizedForm):
    description = TextAreaField('Beschreibung', [InputRequired()])


class ImageCreateForm(LocalizedForm):
    image = FileField('Bilddatei', [InputRequired()])
    caption = StringField('Bildunterschrift', [Optional(), Length(max=200)])
