from django.db import migrations, models



class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),  # Ajusta al nombre de tu migración anterior
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='precio',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0.00),
        ),
    ]