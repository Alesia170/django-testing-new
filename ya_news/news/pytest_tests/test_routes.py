from http import HTTPStatus

import pytest


@pytest.mark.parametrize(
    'url_fixture',
    ('delete_comment_url', 'edit_comment_url'),
)
def test_anonymous_user_is_redirected_to_login(
    client,
    login_url,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


@pytest.mark.parametrize(
    'client_fixture',
    ('client', 'author_client', 'reader_client'),
)
def test_routes_other_users(client_fixture, request, db, subtests):
    test_client = request.getfixturevalue(client_fixture)

    cases = {
        'client': (
            ('home_url', 'get', HTTPStatus.OK),
            ('login_url', 'get', HTTPStatus.OK),
            ('signup_url', 'get', HTTPStatus.OK),
            ('detail_news_url', 'get', HTTPStatus.OK),
            ('logout_url', 'get', HTTPStatus.METHOD_NOT_ALLOWED),
        ),
        'author_client': (
            ('detail_news_url', 'get', HTTPStatus.OK),
            ('edit_comment_url', 'get', HTTPStatus.OK),
            ('delete_comment_url', 'get', HTTPStatus.OK),
            ('logout_url', 'post', HTTPStatus.OK),
        ),
        'reader_client': (
            ('edit_comment_url', 'get', HTTPStatus.NOT_FOUND),
            ('delete_comment_url', 'get', HTTPStatus.NOT_FOUND),
        ),
    }

    for url_fixture, method, expected_status in cases[client_fixture]:
        with subtests.test(url=url_fixture, client=client_fixture):
            url = request.getfixturevalue(url_fixture)
            response = getattr(test_client, method)(url)

            assert response.status_code == expected_status

            if url_fixture == 'logout_url' and method == 'post':
                assert '_auth_user_id' not in test_client.session
