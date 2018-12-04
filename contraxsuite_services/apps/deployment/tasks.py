"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
import datetime
import logging

import requests
from django.utils.timezone import now

import settings
from apps.celery import app
from apps.deployment.models import Deployment
from apps.task.utils.task_utils import TaskUtils

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.6/LICENSE"
__version__ = "1.1.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_NAME = __name__


@app.task(name='deployment.usage_stats', bind=True)
def usage_stats(self):
    TaskUtils.prepare_task_execution()
    d, _created = Deployment.objects.get_or_create(pk=1)  # type: Deployment
    if d.last_report_date and (now() - d.last_report_date) < datetime.timedelta(hours=12):
        return

    resp = None
    data = {'installation_id': str(d.installation_id) if d.installation_id else None,
            'deployment_date': d.deployment_date.isoformat() if d.deployment_date else None,
            'version_number': settings.VERSION_NUMBER,
            'version_commit': settings.VERSION_COMMIT}
    for url in settings.STATS_URLS:
        try:
            resp = requests.post(url, json=data)
        except:
            logging.exception('Unable to run usage_stats try')
        if resp and resp.status_code == 200:
            break

    if not resp or resp.status_code != 200:
        raise usage_stats.retry(countdown=60)
    else:
        d.last_report_date = now()
        d.save()
