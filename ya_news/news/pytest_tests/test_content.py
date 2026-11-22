from http import HTTPStatus

import pytest
from news.forms import CommentForm
from news.pytest_tests.constants import NEWS_ON_PAGE


def test_news_count_on_home_page(news_list, author_client, home_url):

    response = author_client.get(home_url)
    object_list = list(response.context['object_list'])

    assert len(object_list) == NEWS_ON_PAGE


def test_news_are_sorted_newest_first(news_list, author_client, home_url):

    response = author_client.get(home_url)
    news_date = [news.date for news in response.context['object_list']]

    expected_date = sorted([news.date for news in news_list], reverse=True)[
        :NEWS_ON_PAGE
    ]

    assert news_date == expected_date


def test_comments_are_sorted_oldest_first(
    comments_list, author_client, detail_news_url
):

    response = author_client.get(detail_news_url)

    comment_date = [
        comment.created
        for comment in response.context['news'].comment_set.all()
    ]

    expected_date = sorted([comment.created for comment in comments_list])

    assert comment_date == expected_date


@pytest.mark.parametrize(
    'url_fixture',
    ('detail_news_url', 'edit_comment_url'),
)
def test_add_and_edit_news_contain_form(author_client, url_fixture, request):
    url = request.getfixturevalue(url_fixture)

    response = author_client.get(url)

    assert isinstance(response.context['form'], CommentForm)


def test_anonymous_cannot_add_and_edit_news_contain_form(
    client, detail_news_url
):

    response = client.get(detail_news_url)

    assert 'form' not in response.context
    assert response.status_code == HTTPStatus.OK
