from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Medical',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('address', models.CharField(max_length=300)),
                ('tel', models.CharField(max_length=300)),
                ('lot', models.DecimalField(decimal_places=4, max_digits=10)),
                ('lat', models.DecimalField(decimal_places=4, max_digits=10)),
            ],
            options={
                'db_table': 'medical',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MediclaConv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('address', models.CharField(max_length=1000)),
                ('tel', models.CharField(max_length=1000)),
                ('lot', models.DecimalField(decimal_places=7, max_digits=10)),
                ('lat', models.DecimalField(decimal_places=8, max_digits=10)),
            ],
            options={
                'db_table': 'hospital',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=500)),
                ('main', models.CharField(max_length=7000)),
                ('summary', models.CharField(max_length=2000, null=True)),
                ('img_path', models.CharField(max_length=500, null=True)),
                ('publisher', models.CharField(max_length=100, null=True)),
                ('category', models.CharField(max_length=100, null=True)),
                ('url', models.CharField(max_length=200, null=True)),
                ('writedate', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('path', models.CharField(max_length=3000)),
                ('user_id', models.CharField(max_length=100, null=True)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('result0', models.FloatField(max_length=100, null=True)),
                ('result1', models.FloatField(max_length=100, null=True)),
                ('result2', models.FloatField(max_length=100, null=True)),
                ('result3', models.FloatField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('birthday', models.DateField()),
            ],
        ),
    ]
