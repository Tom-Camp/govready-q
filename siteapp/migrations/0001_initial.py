# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-21 19:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Whether the user can log into this admin.')),
                ('is_active', models.BooleanField(default=True, help_text='Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('into_project', models.BooleanField(default=False, help_text='Whether the user being invited is being invited to join from_project.')),
                ('target_object_id', models.PositiveIntegerField()),
                ('target_info', jsonfield.fields.JSONField(blank=True, help_text='Additional information about the target of the invitation.')),
                ('to_email', models.CharField(blank=True, help_text='The email address the invitation was sent to, if to a non-existing user.', max_length=256, null=True)),
                ('text', models.TextField(blank=True, help_text='The personalized text of the invitation.')),
                ('sent_at', models.DateTimeField(blank=True, help_text='If the invitation has been sent by email, when it was sent.', null=True)),
                ('accepted_at', models.DateTimeField(blank=True, help_text='If the invitation has been accepted, when it was accepted.', null=True)),
                ('revoked_at', models.DateTimeField(blank=True, help_text='If the invitation has been revoked, when it was revoked.', null=True)),
                ('email_invitation_code', models.CharField(blank=True, help_text='For emails, a unique verification code.', max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('extra', jsonfield.fields.JSONField(blank=True, help_text='Additional information stored with this object.')),
                ('accepted_user', models.ForeignKey(blank=True, help_text='The user that accepted the invitation (i.e. if the invitation was by email address and an account was created).', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitations_accepted', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='The title of this Project.', max_length=256)),
                ('notes', models.TextField(blank=True, help_text='Notes about this Project for Project members.')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('extra', jsonfield.fields.JSONField(blank=True, help_text='Additional information stored with this object.')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False, help_text='Is the user an administrator of the Project?')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('project', models.ForeignKey(help_text='The Project this is defining membership for.', on_delete=django.db.models.deletion.CASCADE, related_name='members', to='siteapp.Project')),
                ('user', models.ForeignKey(help_text='The user that is a member of the Project.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='invitation',
            name='from_project',
            field=models.ForeignKey(help_text='The Project within which the invitation exists.', on_delete=django.db.models.deletion.CASCADE, related_name='invitations_sent', to='siteapp.Project'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='from_user',
            field=models.ForeignKey(help_text='The User who sent the invitation.', on_delete=django.db.models.deletion.CASCADE, related_name='invitations_sent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invitation',
            name='target_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='invitation',
            name='to_user',
            field=models.ForeignKey(blank=True, help_text='The user who the invitation was sent to, if to an existing user.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitations_received', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='projectmembership',
            unique_together=set([('project', 'user')]),
        ),
    ]
