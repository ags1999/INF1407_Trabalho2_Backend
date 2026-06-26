"""Integração com a API pública do Google Books."""
import requests
from django.conf import settings

BASE_URL = "https://www.googleapis.com/books/v1/volumes"


class GoogleBooksError(Exception):
    """Erro ao consultar a API do Google Books."""


def buscar_livros(query, max_results=10):
    """
    Busca livros no Google Books e devolve uma lista de dicionários
    normalizados (id do volume, título, autor e URL da capa).
    """
    params = {'q': query, 'maxResults': max_results}
    if settings.GBOOKS_API_KEY:
        params['key'] = settings.GBOOKS_API_KEY

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        if status == 503:
            raise GoogleBooksError(
                'O serviço de busca está temporariamente indisponível (503). '
                'Tente novamente mais tarde.'
            ) from exc
        raise GoogleBooksError('Erro ao realizar a busca. Tente novamente.') from exc
    except requests.exceptions.RequestException as exc:
        raise GoogleBooksError(
            'Não foi possível conectar ao serviço de busca.'
        ) from exc

    data = response.json()
    resultados = []
    for item in data.get('items', []):
        info = item.get('volumeInfo', {})
        resultados.append({
            'google_volume_id': item.get('id', ''),
            'title': info.get('title', 'Título Desconhecido'),
            'author': ", ".join(info.get('authors', ['Autor Desconhecido'])),
            'cover_url': info.get('imageLinks', {}).get('thumbnail', ''),
        })
    return resultados
