from django.db import migrations
from apps.users.permissions import document_type_manager_permissions


def add_managers_permissions(apps, _schema_editor):
    DocumentType = apps.get_model('document', 'DocumentType')
    DocumentField = apps.get_model('document', 'DocumentField')
    Permission = apps.get_model('auth', 'Permission')
    CustomUserObjectPermission = apps.get_model('users', 'CustomUserObjectPermission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    document_ctype_id = ContentType.objects.get_for_model(DocumentType).id
    docfield_ctype_id = ContentType.objects.get_for_model(DocumentField).id

    def get_perm_id(permission_name: str, document_ctype_id: int):
        app_label, codename = permission_name.split('.', 1)
        return Permission.objects.get(content_type_id=document_ctype_id,
                                      codename=codename).id

    new_permissions = []

    for doc_type in DocumentType.objects.all():
        for mgr in doc_type.managers.all():
            for perm_name in document_type_manager_permissions['document_type']:
                new_permissions.append((mgr.pk, get_perm_id(perm_name, document_ctype_id),
                                        document_ctype_id, doc_type.pk))
            for doc_field in doc_type.fields.all():
                for perm_name in document_type_manager_permissions['document_field']:
                    new_permissions.append((mgr.pk, get_perm_id(perm_name, docfield_ctype_id),
                                            docfield_ctype_id, doc_field.pk))

    perms = [CustomUserObjectPermission(
        user_id=user_id, permission_id=perm_id, content_type_id=ctype_id, object_pk=object_id)
        for user_id, perm_id, ctype_id, object_id in new_permissions]

    CustomUserObjectPermission.objects.bulk_create(perms, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0218_permissions'),
        ('users', '0023_user_initials'),
    ]

    operations = [
        migrations.RunPython(add_managers_permissions, reverse_code=migrations.RunPython.noop),
    ]
