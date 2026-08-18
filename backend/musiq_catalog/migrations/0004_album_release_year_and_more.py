from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("musiq_catalog", "0003_alter_album_release_year_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="album",
            constraint=models.CheckConstraint(
                check=models.Q(release_year__gte=1860),
                name="ck_album_release_year_gte_1860",
            ),
        ),
        migrations.AddConstraint(
            model_name="albumsong",
            constraint=models.CheckConstraint(
                check=models.Q(track_number__gte=1),
                name="ck_albumsong_track_number_gte_1",
            ),
        ),
    ]
