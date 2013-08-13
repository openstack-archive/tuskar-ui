#!/bin/bash

set -o errexit

HORIZON=${HORIZON-../horizon}

"$HORIZON"/tools/with_venv.sh ./manage.py test tuskar_ui --settings tuskar_ui.test.settings
