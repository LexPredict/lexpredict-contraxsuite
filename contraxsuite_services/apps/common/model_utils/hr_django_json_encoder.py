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

import datetime
import decimal
import inspect
import json
from collections import Set
from json import JSONEncoder
from json.encoder import INFINITY, _make_iterencode, encode_basestring_ascii, encode_basestring
from typing import Any

from django.utils.timezone import is_aware

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


try:
    from _json import make_encoder as c_make_encoder
except ImportError:
    c_make_encoder = None


class HRDjangoJSONEncoder(JSONEncoder):
    """
    HR stands for Human Readable
    We use this class to render some data that is only destined to
    be shown to the end user, e.g. task arguments
    that we don't use in queries etc.

    For custom classes the encoder returns only the class names.
    """
    MAX_ITEM_LENGTH = 128

    def encode(self, o: Any) -> str:
        if o is None:
            return 'None'
        return self.brief_encode(o)

    def brief_encode(self, o: Any) -> str:
        if isinstance(o, str):
            if self.ensure_ascii:
                return brief_encode_basestring_ascii(o)
            return brief_encode_basestring(o)
        # This doesn't pass the iterator directly to ''.join() because the
        # exceptions aren't as detailed.  The list call should be roughly
        # equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(o, _one_shot=True)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return ''.join(chunks)

    def iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string
        representation as available.

        For example::

            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = brief_encode_basestring_ascii
        else:
            _encoder = brief_encode_basestring

        def floatstr(o, allow_nan=self.allow_nan,
                     _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text

        if (_one_shot and c_make_encoder is not None
                and self.indent is None):
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan)
        else:
            _iterencode = _make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot)
        return _iterencode(o, 0)

    def default(self, o: Any) -> Any:
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, Set):
            return dict(_set_object=list(o))
        if isinstance(o, datetime.datetime):
            r = o.isoformat(' ')
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        if isinstance(o, decimal.Decimal):
            return str(o)
        if inspect.isclass(type(o)):
            # is class serializable?
            try:
                json.dumps(o)
            except:
                return type(o).__name__
        return super().default(o)


def brief_encode_basestring_ascii(s):
    text = encode_basestring_ascii(s)
    text = text[:HRDjangoJSONEncoder.MAX_ITEM_LENGTH - 3] + '...' \
        if len(text) > HRDjangoJSONEncoder.MAX_ITEM_LENGTH else text
    return json.dumps(text)


def brief_encode_basestring(s):
    text = encode_basestring(s)
    text = text[:HRDjangoJSONEncoder.MAX_ITEM_LENGTH - 3] + '...' \
        if len(text) > HRDjangoJSONEncoder.MAX_ITEM_LENGTH else text
    return json.dumps(text)
