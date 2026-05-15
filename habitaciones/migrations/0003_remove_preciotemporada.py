from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('habitaciones', '0002_habitacion_activa'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PrecioTemporada',
        ),
    ]