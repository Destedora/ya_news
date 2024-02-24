from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def new():
    new = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return new


@pytest.fixture
def comment(author, new):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def new_id_for_args(new):
    return new.id,


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def news_more_than_on_page():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments_with_different_dates(new, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=new, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
