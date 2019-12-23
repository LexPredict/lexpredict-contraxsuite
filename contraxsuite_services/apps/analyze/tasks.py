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
# -*- coding: utf-8 -*-

from apps.celery import app
from apps.analyze.ml.transform import Doc2VecTransformer
from apps.task.tasks import BaseTask

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


MODULE_NAME = __name__


class TrainDoc2VecModel(BaseTask):
    name = 'Train doc2vec Model'
    priority = 9

    def process(self, **kwargs):
        source = kwargs.get('source')

        self.log_info(
            'Going to train doc2vec model from {} objects...'.format(source.upper()))

        transformer_name = kwargs.get('transformer_name')
        project_ids = kwargs.get('project_ids')

        vector_size = kwargs.get('vector_size')
        window = kwargs.get('window')
        min_count = kwargs.get('min_count')
        dm = kwargs.get('dm')

        transformer = Doc2VecTransformer(vector_size=vector_size, window=window,
                                         min_count=min_count, dm=dm)

        model_builder_args = dict(project_ids=project_ids, transformer_name=transformer_name)
        if source == 'document':
            model_builder = transformer.build_doc2vec_document_model
        else:
            model_builder = transformer.build_doc2vec_text_unit_model
            model_builder_args['text_unit_type'] = kwargs.get('text_unit_type')

        model_builder(**model_builder_args)


app.register_task(TrainDoc2VecModel())
