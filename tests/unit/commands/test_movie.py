from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.movie import cli


def test_movie(runner):
    result = runner.invoke(cli, ["movie"])
    assert result.exit_code == 0


class TestMovieShow(object):
    def test_valid(self, runner, make_client):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "name": "movie"
                }

            """
        )

        client_mock = make_client()
        result = runner.invoke(cli, ["movie", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["movie", "show"], "Error: Missing argument 'MOVIE_ID'"),
            (["movie", "show", "not_value"], "Error: Invalid value for 'MOVIE_ID'"),
        ],
    )
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def test_with_error(self, runner, make_client):
        client_mock = make_client(with_exception=True)
        result = runner.invoke(cli, ["movie", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: \n"

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(with_exception=False):
            client_mock = mocker.MagicMock()
            if with_exception:
                client_mock.return_value.get_movie.side_effect = RequestsError()
            else:
                client_mock.return_value.get_movie.return_value = {
                    "id": 1,
                    "name": "movie",
                }
            mocker.patch("anymotion_cli.commands.movie.get_client", client_mock)
            return client_mock

        return _make_client


class TestMovieList(object):
    def test_valid(self, runner, make_client):
        expected = dedent(
            """\

                [
                  {
                    "id": 1,
                    "name": "movie"
                  }
                ]

            """
        )

        client_mock = make_client()

        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, runner, make_client):
        client_mock = make_client(num_data=10)

        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"id": 10' in result.output

    def test_with_error(self, runner, make_client):
        client_mock = make_client(with_exception=True)
        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(num_data=1, with_exception=False):
            client_mock = mocker.MagicMock()
            if with_exception:
                client_mock.return_value.get_movies.side_effect = RequestsError()
            else:
                data = [{"id": i + 1, "name": "movie"} for i in range(num_data)]
                client_mock.return_value.get_movies.return_value = data
            mocker.patch("anymotion_cli.commands.movie.get_client", client_mock)
            return client_mock

        return _make_client
