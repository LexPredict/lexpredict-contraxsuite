from collections import defaultdict
from decimal import Decimal
from typing import Any, List, Optional

import dateparser
from django.db import migrations, transaction


class FieldValuePopulator:
    """
            At the moment of creating this migration there were the following field types:
            StringField(),
            StringFieldWholeValueAsAToken(),
            LongTextField(),
            IntField(),
            BooleanField(),
            FloatField(),
            DateTimeField(),
            DateField(),
            RecurringDateField(),
            CompanyField(),
            DurationField(),
            PercentField(),
            RatioField(),
            AddressField(),
            RelatedInfoField(),
            ChoiceField(),
            MultiChoiceField(),
            PersonField(),
            AmountField(),
            MoneyField(),
            GeographyField(),
            LinkedDocumentsField()

            Multi-value field types are: RelatedInfoField, MultiChoiceField, LinkedDocumentsField
            """

    CHUNK_SIZE = 1000

    def __init__(self,
                 apps,
                 schema_editor):
        self.db_alias = schema_editor.connection.alias
        self.Document = apps.get_model('document', 'Document')
        self.FieldValue = apps.get_model('document', 'FieldValue')
        self.FieldAnnotation = apps.get_model('document', 'FieldAnnotation')
        self.FieldAnnotationFalseMatch = apps.get_model('document', 'FieldAnnotationFalseMatch')
        self.DocumentFieldValue = apps.get_model('document', 'DocumentFieldValue')

    def migrate_values(self):
        for doc in self.Document.objects.all().iterator():
            self.migrate_field_values(doc)

    def merge_dfv_values(self, field_type: str, dfv_values: List[Any]) -> Any:
        if field_type == 'related_info':
            return bool(dfv_values)
        elif field_type == 'multi_choice':
            return sorted(set(dfv_values)) if dfv_values else None
        elif field_type == 'linked_documents':
            return sorted(set(dfv_values)) if dfv_values else None
        else:
            return next(iter(dfv_values)) if dfv_values else None

    def to_float(self, v, decimal_places=None) -> Optional[float]:
        """
        Take care about proper rounding for floats:
        round(float('123.5555555'), 6)
        Out[1]: 123.555555
        vs
        to_float('123.5555555', 6)
        Out[2]: 123.555556
        """
        if v is None:
            return None
        v = Decimal(v)
        if isinstance(decimal_places, int):
            v = round(v, decimal_places).normalize()
        return float(v)

    def to_int(self, v) -> Optional[int]:
        return int(v) if v is not None else None

    def dfv_db_value_to_ant_json_value(self, field_type: str, dfv_db_value: Any) -> Any:
        if field_type == 'related_info':
            return True
        elif field_type == 'linked_documents':
            return int(dfv_db_value) if dfv_db_value else None
        elif field_type == 'boolean':
            return bool(dfv_db_value)
        elif field_type == 'datetime':
            return dateparser.parse(str(dfv_db_value)).isoformat() if dfv_db_value else None
        elif field_type in ('date', 'date_recurring'):
            return dateparser.parse(str(dfv_db_value)).date().isoformat() if dfv_db_value else None
        elif field_type == 'float':
            return self.to_float(dfv_db_value) if dfv_db_value is not None else None
        elif field_type == 'int':
            return self.to_int(dfv_db_value) if dfv_db_value is not None else None
        elif field_type == 'address':
            return {'address': dfv_db_value} if dfv_db_value is not None else None
        elif field_type == 'company':
            return dfv_db_value
        elif field_type == 'duration':
            return self.to_float(dfv_db_value) if dfv_db_value is not None else None
        elif field_type == 'percent':
            return self.to_float(dfv_db_value * 100, decimal_places=6) if dfv_db_value is not None else None
        elif field_type == 'ratio':
            if isinstance(dfv_db_value, dict):
                return dfv_db_value
            elif isinstance(dfv_db_value, str) and '|' in dfv_db_value:
                ar = dfv_db_value.split('|')
                numerator_str = ar[0]
                consequent_str = ar[1]
                return {
                    'numerator': self.to_float(numerator_str),
                    'consequent': self.to_float(consequent_str)
                }
        elif field_type == 'amount':
            return self.to_float(dfv_db_value) if dfv_db_value is not None else None
        elif field_type == 'money':
            if isinstance(dfv_db_value, dict):
                return {
                    'currency': dfv_db_value.get('currency'),
                    'amount': self.to_float(dfv_db_value.get('amount'))
                }
            elif isinstance(dfv_db_value, str) and '|' in dfv_db_value:
                ar = dfv_db_value.split('|')
                currency = ar[0]
                amount_str = ar[1]  # type: str
                return {
                    'currency': currency,
                    'amount': self.to_float(amount_str)
                }
        else:
            return dfv_db_value

    def migrate_field_values(self, doc: 'Document') -> int:
        with transaction.atomic():
            doc_dfvs = list(self.DocumentFieldValue.objects.filter(document=doc).prefetch_related('field'))
            if not doc_dfvs:
                return 0

            doc_dfvs_by_field = defaultdict(list)
            for dfv in doc_dfvs:
                doc_dfvs_by_field[dfv.field].append(dfv)

            false_matches = list()
            ants = list()
            field_values = list()

            for field, dfvs in doc_dfvs_by_field.items():
                ant_values = list()
                last_modified_by = None
                last_modified_date = None
                for dfv in dfvs:
                    dfv_modified_date = dfv.modified_date or dfv.created_date
                    dfv_modified_by = dfv.modified_by or dfv.created_by
                    if last_modified_date is None or last_modified_date < dfv_modified_date:
                        last_modified_date = dfv_modified_date
                        last_modified_by = dfv_modified_by

                    # calculating annotation values - in the final json format
                    ant_value = self.dfv_db_value_to_ant_json_value(field.type, dfv.value)

                    # and collecting them for further calculating the field value
                    # - but only those not removed by users
                    if not dfv.removed_by_user:
                        ant_values.append(ant_value)

                    # for DocumentFieldValues with location - creating annotations or false matches
                    if dfv.location_start is not None and dfv.location_end is not None:
                        location_text = doc.full_text[dfv.location_start:dfv.location_end]
                        if dfv.removed_by_user:
                            false_matches.append(self.FieldAnnotationFalseMatch(document=doc,
                                                                                field=field,
                                                                                value=ant_value,
                                                                                location_start=dfv.location_start,
                                                                                location_end=dfv.location_end,
                                                                                location_text=location_text,
                                                                                text_unit=dfv.text_unit))
                        else:
                            ants.append(self.FieldAnnotation(document=doc,
                                                             field=field,
                                                             value=ant_value,
                                                             location_start=dfv.location_start,
                                                             location_end=dfv.location_end,
                                                             location_text=location_text,
                                                             text_unit=dfv.text_unit,
                                                             extraction_hint=dfv.extraction_hint,
                                                             modified_date=dfv_modified_date,
                                                             modified_by=dfv_modified_by))

                field_value_json = self.merge_dfv_values(field.type, ant_values) if dfvs else None
                field_values.append(self.FieldValue(document=doc,
                                                    field=field,
                                                    value=field_value_json,
                                                    modified_date=last_modified_date,
                                                    modified_by=last_modified_by
                                                    ))

            self.FieldAnnotation.objects.filter(document=doc).delete()
            self.FieldAnnotationFalseMatch.objects.filter(document=doc).delete()
            self.FieldValue.objects.filter(document=doc).delete()

            self.FieldAnnotation.objects.bulk_create(ants)
            self.FieldAnnotationFalseMatch.objects.bulk_create(false_matches)
            self.FieldValue.objects.bulk_create(field_values)

            print(f'For document {doc.name} (#{doc.pk}) created:\n'
                  f'- annotations:               {len(ants)}\n'
                  f'- annotations false matches: {len(false_matches)}\n'
                  f'- field values:              {len(field_values)}')


def populate_field_values(apps, schema_editor):
    mgr = FieldValuePopulator(apps, schema_editor)
    mgr.migrate_values()


class Migration(migrations.Migration):
    dependencies = [
        ('document', '0156_auto_20191002_0835'),
    ]

    operations = [
        migrations.RunPython(populate_field_values,
                             reverse_code=migrations.RunPython.noop),
    ]
