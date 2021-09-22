from django.db import migrations, connection, models


def run_migration(_apps, _schema_editor):
    with connection.cursor() as cursor:
        cursor.execute('''
        create or replace function calc_task_progress(src_id varchar, 
                                              src_own_progress int, 
                                              src_own_status varchar,
                                              src_has_sub_tasks boolean) returns float as $$
        begin
            if not src_has_sub_tasks then
                return fix_task_progress_with_status(greatest(0, least(coalesce(src_own_progress, 0), 100)), task_status_precedence(src_own_status));
            else
                return (select avg(  (case when ch.id = src_id 
                                        then fix_task_progress_with_status(greatest(0, least(coalesce(ch.own_progress, 0), 100)), task_status_precedence(ch.own_status)) 
                                        else calc_task_progress(ch.id, ch.own_progress, ch.own_status, ch.has_sub_tasks)
                                        end) * coalesce(ch.weight, 100) ) / sum(coalesce(ch.weight, 100)) 
                            from task_task ch 
                            where     not ch.run_if_parent_task_failed 
                                  and (ch.parent_task_id = src_id or ch.id = src_id));
            end if;
        end;
    $$ language plpgsql;''')


def revert_migration(_apps, _schema_editor):
    with connection.cursor() as cursor:
        cursor.execute('''
        create or replace function calc_task_progress(src_id varchar, 
                                                      src_own_progress int, 
                                                      src_own_status varchar,
                                                      src_has_sub_tasks boolean) returns float as $$
            begin
                if not src_has_sub_tasks then
                    return fix_task_progress_with_status(greatest(0, least(coalesce(src_own_progress, 0), 100)), task_status_precedence(src_own_status));
                else
                    return (select avg(case when ch.id = src_id 
                                            then fix_task_progress_with_status(greatest(0, least(coalesce(ch.own_progress, 0), 100)), task_status_precedence(ch.own_status)) 
                                            else calc_task_progress(ch.id, ch.own_progress, ch.own_status, ch.has_sub_tasks)
                                            end) 
                                from task_task ch 
                                where     not ch.run_if_parent_task_failed 
                                      and (ch.parent_task_id = src_id or ch.id = src_id));
                end if;
            end;
        $$ language plpgsql;''')


class Migration(migrations.Migration):
    dependencies = [
        ('task', '0073_remove_dirty_from_task_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='weight',
            field=models.PositiveIntegerField(blank=True, default=100, null=True),
        ),
        migrations.RunPython(run_migration, reverse_code=revert_migration)
    ]
