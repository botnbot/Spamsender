from django.conf import settings
from django.db import models
from django.utils import timezone


# Create your models here.

class Message(models.Model):
    subject = models.CharField(max_length=150, verbose_name="Тема")
    text = models.TextField(verbose_name="Содержание")

    def __str__(self):
        return f"Тема {self.subject}"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        permissions = [
            ("view_all_messages", "Может просматривать все сообщения"),
        ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='messages',
                              verbose_name='Владелец'
                              )


class Recipient(models.Model):
    email = models.EmailField(verbose_name='email')
    name = models.CharField(max_length=150, verbose_name='Имя')
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='recipients',
                              verbose_name='Владелец'
                              )

    def __str__(self):
        return f"{self.name} <{self.email}>"

    class Meta:
        unique_together = [("email", "owner")]
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        permissions = [
            ("view_all_recipients", "Может просматривать всех получателей"),
        ]


class NewsletterQuerySet(models.QuerySet):
    def with_updated_status(self):
        for obj in self:
            obj.update_status()
        return self


class Newsletter(models.Model):
    STATUS_CREATED = "created"
    STATUS_STARTED = "started"
    STATUS_FINISHED = "finished"

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_FINISHED, 'Завершена'),
    ]

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_CREATED)
    start_time = models.DateTimeField(verbose_name="Дата начала отправки")
    last_send_time = models.DateTimeField(verbose_name="Дата окончания отправки")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='newsletters',
        verbose_name='Владелец'
    )
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
        return f"Рассылка {self.id}— {self.get_status_display()}"

    def update_status(self):
        now = timezone.now()

        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.last_send_time:
            new_status = self.STATUS_STARTED
        else:
            new_status = self.STATUS_FINISHED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = ('-start_time',)
        permissions = [
            ("view_all_newsletters", "Может просматривать все рассылки"),
        ]

    objects = NewsletterQuerySet.as_manager()


class SendAttempt(models.Model):
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки отправки")
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, null=True, blank=True)
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('fail', 'Не успешно'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='fail')
    smtp_answer = models.TextField(blank=True, null=True, verbose_name='Ответ сервера')

    newsletter = models.ForeignKey(
        to="Newsletter",
        on_delete=models.CASCADE,
        verbose_name="рассылка",
        related_name="attempts",
    )

    class Meta:
        verbose_name = "попытка"
        verbose_name_plural = "попытки"
        ordering = ('-attempt_time',)

    def __str__(self):
        return f" {self.attempt_time} {self.status}"
