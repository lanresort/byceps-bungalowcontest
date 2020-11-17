==========================
LANresort Bungalow Contest
==========================

At our LANresort_ events, which are LAN parties in holiday village
bungalows, we have the "bungalow contest". Participants can present
their decorated bungalows and all attendees can rate them.

This repository contains code that extends the BYCEPS_ LAN party
platform to provide a user frontend to register and vote for bungalows
as well as an admin UI to manage the contest and see the partially
aggregated ratings.

The implementation depends on the actual bungalow system (specifically,
the "bungalow occupation" entity, which is the information that a
bungalow is occupied and by which users), but that has not been
open-sourced (at this point), though.

**However**, it should be easy to make the contest system independent of
the bungalow system by cutting out the connection to the bungalow
occupation.

There can be one contest per party.

While the contest system does not work independently right out of the
box, it serves an example of how an extension to BYCEPS can look like.

.. _LANresort: https://www.lanresort.de/
.. _BYCEPS: https://byceps.nwsnet.de/


Installation
============

To integrate this with BYCEPS:

- Drop the code into a BYCEPS installation.
- Register the blueprints (in ``byceps/blueprints/blueprints.py``):

  - site blueprint: ``site.bungalow_contest`` to URL path
    ``/bungalow-contest``

  - admin blueprint: ``admin.bungalow_contest`` to URL path
    ``/admin/bungalow-contest``

- Link to those URL paths in your party website's and the admin UI's
  respective navigations.


License
=======

The code is licensed under the terms of the Revised BSD license (see
``LICENSE`` file for details).
