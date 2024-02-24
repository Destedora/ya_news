import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, news_more_than_on_page):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_more_than_on_page):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(
        client, comments_with_different_dates, new_id_for_args
        ):
    url = reverse('news:detail', args=new_id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, new_id_for_args):
    detail_url = reverse('news:detail', args=new_id_for_args)
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, new_id_for_args):
    detail_url = reverse('news:detail', args=new_id_for_args)
    response = author_client.get(detail_url)
    assert 'form' in response.context
