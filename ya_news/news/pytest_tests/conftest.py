from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News
from news.pytest_tests.constants import COMMENT_COUNT, NEWS_DATE, NEWS_ON_PAGE


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
    )


@pytest.fixture
def comment(author, news, db):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def news_list(db):
    return News.objects.bulk_create(
        (
            News(
                title=f'Новость {index}',
                text='Текст новости',
                date=NEWS_DATE + timedelta(days=index),
            )
            for index in range(NEWS_ON_PAGE + 1)
        )
    )


@pytest.fixture
def comments_list(author, news, db):
    current_time = timezone.now()

    comments = Comment.objects.bulk_create(
        (
            Comment(
                news=news,
                author=author,
                text=f'Комментарий {index} с различающимся временем создания',
            )
            for index in range(COMMENT_COUNT)
        )
    )

    for index, comment in enumerate(comments):
        comment.created = current_time - timedelta(days=index)

    Comment.objects.bulk_update(comments, ('created',))

    return comments


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_news_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.pk,))
