from http import HTTPStatus

from news.models import Comment
from news.pytest_tests.constants import (FORBIDDEN_WORDS_ERROR, FORM_DATA,
                                         FORM_DATA_EDIT, INVALID_COMMENT)


def test_anonymous_cannot_add_comment(client, detail_news_url):

    existing_ids = set(Comment.objects.values_list('pk', flat=True))

    response = client.post(detail_news_url, data=FORM_DATA)
    created_comment = Comment.objects.exclude(pk__in=existing_ids)

    assert created_comment.count() == 0
    assert response.status_code == HTTPStatus.FOUND


def test_author_add_comment(author_client, author, detail_news_url, news):

    existing_ids = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(detail_news_url, data=FORM_DATA)

    created_comment = Comment.objects.exclude(pk__in=existing_ids)

    comment = created_comment.get()

    assert created_comment.count() == 1
    assert comment.text == FORM_DATA['text']
    assert comment.author == author
    assert comment.news == news
    assert response.status_code == HTTPStatus.FOUND


def test_add_comment_redirect_to_news_detail(author_client, detail_news_url):

    response = author_client.post(detail_news_url, data=FORM_DATA)

    expected_url = detail_news_url + '#comments'

    assert response.url == expected_url
    assert response.status_code == HTTPStatus.FOUND


def test_edit_comment_redirect_to_news_detail(
    author_client, detail_news_url, edit_comment_url
):

    response = author_client.post(edit_comment_url, data=FORM_DATA_EDIT)
    expected_url = detail_news_url + '#comments'

    assert response.url == expected_url
    assert response.status_code == HTTPStatus.FOUND


def test_delete_comment_redirect_to_news_detail(
    author_client, detail_news_url, delete_comment_url
):

    response = author_client.post(delete_comment_url)

    expected_url = detail_news_url + '#comments'

    assert response.url == expected_url
    assert response.status_code == HTTPStatus.FOUND


def test_invalid_comment_shows_error_message(author_client, detail_news_url):
    comments_before = Comment.objects.count()

    response = author_client.post(detail_news_url, data=INVALID_COMMENT)

    form = response.context['form']

    assert FORBIDDEN_WORDS_ERROR in form.errors['text']
    assert Comment.objects.count() == comments_before


def test_author_edit_comment_do_not_change_author(
    author, author_client, edit_comment_url, news, comment
):
    comment_id = comment.pk
    response = author_client.post(edit_comment_url, FORM_DATA_EDIT)

    updated_comment = Comment.objects.get(pk=comment_id)

    assert updated_comment.author == author
    assert updated_comment.news == news
    assert updated_comment.text == FORM_DATA_EDIT['text']
    assert response.status_code == HTTPStatus.FOUND


def test_author_can_delete_his_comment(
    author_client, delete_comment_url, comment
):
    comment_id = comment.pk
    author_client.post(delete_comment_url)

    assert not Comment.objects.filter(pk=comment_id).exists()


def test_reader_cannot_edit_delete_other_comments(
    reader_client,
    edit_comment_url,
    delete_comment_url,
    comment,
):
    comment_id = comment.pk
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news

    response = reader_client.post(edit_comment_url, data=FORM_DATA_EDIT)
    updated_comment = Comment.objects.get(pk=comment.pk)

    assert updated_comment.text == original_text
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news
    assert response.status_code == HTTPStatus.NOT_FOUND

    response_delete = reader_client.post(delete_comment_url)

    assert response_delete.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment_id).exists()
