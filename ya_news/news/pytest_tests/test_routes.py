from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'url_name',
    ('news:home', 'users:login', 'users:signup'),
)
def test_news_are_available(client, db, url_name):
    url = reverse(url_name)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    ('detail_news_url', 'delete_comment_url', 'edit_comment_url'),
)
def test_news_author_can_delete_or_edit(author_client, request, url_fixture):
    url = request.getfixturevalue(url_fixture)

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    ('delete_comment_url', 'edit_comment_url'),
)
def test_news_user_cannot_delete_or_edit(reader_client, request, url_fixture):
    url = request.getfixturevalue(url_fixture)

    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_fixture',
    ('delete_comment_url', 'edit_comment_url'),
)
def test_anonymous_user_is_redirected_to_login(
    client,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_logout_accepts_post_request(author_client, logout_url):

    response = author_client.post(logout_url)

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


def test_logout_rejects_get_request(client, logout_url):

    response = client.get(logout_url)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
