from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0008_product_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Chờ xử lý'),
                    ('shipping', 'Đang vận chuyển'),
                    ('completed', 'Hoàn thành'),
                    ('return', 'Trả hàng/Hoàn tiền'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
