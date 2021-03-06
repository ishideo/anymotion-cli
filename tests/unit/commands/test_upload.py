import pytest
from anymotion_sdk import FileTypeError, RequestsError

from anymotion_cli.commands.upload import cli


class TestUpload(object):
    @pytest.mark.parametrize(
        "file_name, media_type",
        [("image.jpg", "image"), ("movie.mp4", "movie")],
    )
    def test_valid(self, runner, make_path, make_client, file_name, media_type):
        path = make_path(file_name, is_file=True)
        expected = (
            f"Success: Uploaded {path} to the cloud storage. ({media_type} id: 1)\n"
        )
        client_mock = make_client(media_type=media_type)

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 0
        assert result.output == expected
        assert client_mock.call_count == 1

    def test_with_RequestsError(self, runner, make_path, make_client):
        path = make_path("image.jpg", is_file=True)
        client_mock = make_client(with_requests_error=True)

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 1
        assert result.output == "Error: \n"
        assert client_mock.call_count == 1

    def test_with_FileTypeError(self, runner, make_path, make_client):
        path = make_path("image.jpg", is_file=True)
        client_mock = make_client(with_file_type_error=True)

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 2
        assert result.output.endswith("Error: Invalid value: \n")
        assert client_mock.call_count == 1

    def test_invalid_params(self, runner, make_client):
        client_mock = make_client()

        result = runner.invoke(cli, ["upload"])

        assert result.exit_code == 2
        assert result.output.endswith("Error: Missing argument 'PATH'.\n")
        assert client_mock.call_count == 0

    @pytest.mark.parametrize(
        "file_name, is_file, is_dir, exists, expected",
        [
            (
                "image.jpg",
                True,
                False,
                False,
                "Error: Invalid value for 'PATH': File '{}' does not exist.\n",
            ),
            (
                "dir",
                False,
                True,
                False,
                "Error: Invalid value for 'PATH': File '{}' does not exist.\n",
            ),
            (
                "dir",
                False,
                True,
                True,
                "Error: Invalid value for 'PATH': File '{}' is a directory.\n",
            ),
        ],
    )
    def test_invalid_path(
        self,
        runner,
        make_path,
        make_client,
        file_name,
        is_file,
        is_dir,
        exists,
        expected,
    ):
        path = make_path(file_name, is_file=is_file, is_dir=is_dir, exists=exists)
        expected = expected.format(path)
        client_mock = make_client()

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 2
        assert result.output.endswith(expected)
        assert client_mock.call_count == 0

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(
            media_type="image", with_file_type_error=False, with_requests_error=False
        ):
            client_mock = mocker.MagicMock()

            if with_file_type_error:
                client_mock.return_value.upload.side_effect = FileTypeError()
            elif with_requests_error:
                client_mock.return_value.upload.side_effect = RequestsError()
            elif media_type == "image":
                client_mock.return_value.upload.return_value.image_id = 1
                client_mock.return_value.upload.return_value.movie_id = None
            else:
                client_mock.return_value.upload.return_value.image_id = None
                client_mock.return_value.upload.return_value.movie_id = 1

            mocker.patch("anymotion_cli.commands.upload.get_client", client_mock)

            return client_mock

        return _make_client
