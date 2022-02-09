from django.db import migrations


def update_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, _ = Group.objects.get_or_create(name="Project and Document Type Creator")
    try:
        group.permissions.add(Permission.objects.get(content_type__app_label='task',
                                                     content_type__model='task',
                                                     codename='add_task'))
    except:
        pass

    try:
        group.permissions.add(Permission.objects.get(content_type__app_label='task',
                                                     content_type__model='task',
                                                     codename='view_task'))
    except:
        pass


def remove_perms_from_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, _ = Group.objects.get_or_create(name="Project and Document Type Creator")
    try:
        group.permissions.remove(Permission.objects.get(content_type__app_label='task',
                                                        content_type__model='task',
                                                        codename='add_task'))
    except:
        pass

    try:
        group.permissions.remove(Permission.objects.get(content_type__app_label='task',
                                                        content_type__model='task',
                                                        codename='view_task'))
    except:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_add_task_permissions_to_project_creator_group'),
    ]

    operations = [
        migrations.RunPython(update_group, reverse_code=remove_perms_from_group),
    ]
