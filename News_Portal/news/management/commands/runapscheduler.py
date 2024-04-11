import logging
from datetime import datetime, timedelta
from django.utils import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.defaultfilters import truncatewords_html
from django.utils.html import format_html
from django.core.mail import EmailMultiAlternatives
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Post, Subscription

logger = logging.getLogger(__name__)


def my_job():
    last_week = datetime.now() - timedelta(weeks=1)
    aware_datetime = timezone.make_aware(last_week)

    subscriptions = Subscription.objects.all()

    for subscription in subscriptions:
        posts = Post.objects.filter(
            categories=subscription.category,
            published__gte=aware_datetime
        ).order_by('published')

        if posts:
            separator = '<hr>'
            html_content = '<h1>Новые статьи в вашей подписке:</h1>'
            for post in posts:
                truncated_content = truncatewords_html(post.content, 10)
                article_link = format_html(
                    '<a href="{}">{}</a>',
                    f"{settings.SITE_DOMAIN}{post.get_absolute_url()}",
                    post.title
                )
                html_content += f'<h2>{article_link}</h2>'
                html_content += f'<p>{truncated_content}</p>'
                html_content += separator

            # Удаляем последний разделитель
            html_content = html_content[:-len(separator)]

            subject = "Новые статьи в вашей подписке"
            msg = EmailMultiAlternatives(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [subscription.user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week='fri', hour=18, minute=00),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
