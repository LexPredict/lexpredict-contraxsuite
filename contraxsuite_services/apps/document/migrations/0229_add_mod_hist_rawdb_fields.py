import datetime
from typing import Dict, Optional

from django.db import migrations, models, connection

FIELD_CODE_CREATED_BY = ('created_by', 'character varying')
FIELD_CODE_MODIFIED_DATE = ('modified_date', 'timestamp with time zone')
FIELD_CODE_MODIFIED_BY = ('modified_by', 'character varying')


def migrate_rawdb_fields(_apps, _schema_editor):
    from apps.rawdb.repository.raw_db_migrations import add_rawdb_migration_column
    for field, code in [FIELD_CODE_CREATED_BY, FIELD_CODE_MODIFIED_DATE, FIELD_CODE_MODIFIED_BY]:
        add_rawdb_migration_column(field, code)

    # read user names
    user_name_by_id = {}
    with connection.cursor() as cursor:
        cursor.execute('''select id, name, first_name, last_name, username from users_user;''')
        for id, name, first_name, last_name, username in cursor.fetchall():
            usr_name = name
            if not usr_name:
                if first_name and last_name:
                    full_name = '%s %s' % (first_name, last_name)
                    return full_name.strip()
                else:
                    usr_name = username
            user_name_by_id[id] = usr_name

    # fill values
    project_table_by_id: Dict[int, str] = {}

    with connection.cursor() as cursor:
        cursor.execute('''select uid, project_id, created_date, created_by_id from project_uploadsession;''')
        for session_id, project_id, created_date, created_by_id in cursor.fetchall():
            usr_name = user_name_by_id.get(created_by_id or 0) or ''
            table_name = project_table_by_id.get(project_id, None)
            if table_name is None:
                table_name = find_cache_table_by_project_id(project_id, cursor)
                project_table_by_id[project_id] = table_name
            if not table_name:
                continue
            update_documents_by_session_data(cursor, session_id, table_name, created_date, usr_name)


def update_documents_by_session_data(cursor,
                                     upload_session_id: str,
                                     table_name: str,
                                     created_date: Optional[datetime.datetime],
                                     created_by: Optional[str]):
    cursor.execute(f'''
        UPDATE "{table_name}" p
        SET {FIELD_CODE_CREATED_BY[0]} = %s, {FIELD_CODE_MODIFIED_DATE[0]} = %s, {FIELD_CODE_MODIFIED_BY[0]} = %s
        FROM 
            document_document d
        WHERE 
            p.document_id = d.id AND d.upload_session_id = %s;
    ''', [created_by, created_date, created_by, upload_session_id])


def find_cache_table_by_project_id(project_id: int, cursor) -> str:
    from apps.rawdb.repository.raw_db_repository import doc_fields_table_name
    from apps.rawdb.repository.raw_db_migrations import check_table_exists

    cursor.execute('''select pt.code from document_documenttype pt 
         join project_project p on p.type_id = pt.uid where p.id = %s;''', [project_id])
    codes = [p[0] for p in cursor.fetchall()]
    if not codes:
        return ''

    cache_table_name = doc_fields_table_name(codes[0])
    if not check_table_exists(cursor, cache_table_name):
        return ''
    return cache_table_name


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0228_auto_20210210_1241'),
    ]

    operations = [
        migrations.RunPython(migrate_rawdb_fields, reverse_code=migrations.RunPython.noop)
    ]
