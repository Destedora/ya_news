import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, new_id_for_args):
    url = reverse('news:detail', args=new_id_for_args)
    client.post(url, data={'text': 'Текст комментария'})
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author, author_client, new_id_for_args, new):
    url = reverse('news:detail', args=new_id_for_args)
    response = author_client.post(url, data={'text': 'Текст комментария'})
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == 'Текст комментария'
    assert comment.news == new
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, new_id_for_args):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=new_id_for_args)
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
        )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client, new_id_for_args, comment_id_for_args
        ):
    delete_url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.delete(delete_url)
    news_url = reverse('news:detail', args=new_id_for_args)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        admin_client, comment_id_for_args
        ):
    delete_url = reverse('news:delete', args=comment_id_for_args)
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, comment_id_for_args, new_id_for_args, comment
        ):
    edit_url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(
        edit_url, data={'text': 'Обновлённый комментарий'}
    )
    news_url = reverse('news:detail', args=new_id_for_args)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'Обновлённый комментарий'


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment_id_for_args, comment
):
    edit_url = reverse('news:edit', args=comment_id_for_args)
    response = admin_client.post(
        edit_url, data={'text': 'Обновлённый комментарий'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
