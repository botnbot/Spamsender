from django.db import models


# Create your models here.

class Message(models.Model):
    subject = models.CharField(max_length=150, verbose_name="Тема")
    text = models.TextField(verbose_name="Содержание")

    def __str__(self):
        return f"Тема {self.subject}"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='email')
    name = models.CharField(max_length=150, verbose_name='Имя')
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.name} <{self.email}>"

    class Meta:
        verbose_name = "получатель"
        verbose_name_plural = "получатели"


class Newsletter(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('active', 'Активна'),
        ('completed', 'Завершена'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='completed')
    first_send_time = models.DateTimeField(verbose_name="Дата первой отправки")
    last_send_time = models.DateTimeField(verbose_name="Дата окончания отправки")
    message = models.ForeignKey(
        to="Message",
        on_delete=models.CASCADE,
        verbose_name="Сообщение",
        related_name="newsletters",
    )
    recipients = models.ManyToManyField(
        to="Recipient",
        verbose_name="Получатели",
        related_name="newsletters",
    )

    def __str__(self):
        return f"Рассылка {self.message.subject} {self.status}"

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = ('-first_send_time',)
