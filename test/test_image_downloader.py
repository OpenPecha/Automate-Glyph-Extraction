import os
import boto3
import configparser
import pytest
from moto import mock_aws
from pathlib import Path
from unittest.mock import patch
from tools.image_downloader import remove_non_page, get_random_images_dict, download_and_save_image
from unittest.mock import patch


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

@pytest.fixture
def s3_client(aws_credentials):
    with mock_aws():
        conn = boto3.client('s3', region_name='us-east-1')
        conn.create_bucket(Bucket='archive.tbrc.org')
        yield conn

@pytest.fixture
def config():
    """Mocked ConfigParser for testing."""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'mock_config.ini')
    config.read(config_path)
    return config

def test_remove_non_page():
    images_list = [{'filename': '001.jpg'}, {'filename': '002.jpg'}, {'filename': '009.jpg'}, {'filename': '010.jpg'}]
    work_id = 'W123'
    image_group_id = 'I1'
    result = remove_non_page(images_list, work_id, image_group_id)
    assert result == ['Works/23/W123/images/W123-I1/009.jpg', 'Works/23/W123/images/W123-I1/010.jpg']

@patch('your_script.get_buda_scan_info')
@patch('your_script.get_image_list')
@patch('your_script.is_archived')
def test_get_random_images_dict(mock_is_archived, mock_get_image_list, mock_get_buda_scan_info, s3_client, config):
    mock_get_buda_scan_info.return_value = {"image_groups": {"I1": "Some info"}}
    mock_get_image_list.return_value = [{'filename': '009.jpg'}, {'filename': '010.jpg'}]
    mock_is_archived.return_value = True

    work_id = 'W123'
    bucket_name = 'archive.tbrc.org'
    result = get_random_images_dict(work_id, s3_client, bucket_name, config)
    expected = {'I1': ['Works/23/W123/images/W123-I1/009.jpg', 'Works/23/W123/images/W123-I1/010.jpg']}
    assert result == expected

def test_download_and_save_image(s3_client, config, tmp_path):
    bucket_name = 'archive.tbrc.org'
    obj_dict = {'I1': ['Works/23/W123/images/W123-I1/009.jpg', 'Works/23/W123/images/W123-I1/010.jpg']}
    save_path = tmp_path

    s3_client.put_object(Bucket=bucket_name, Key='Works/23/W123/images/W123-I1/009.jpg', Body=b'Test Data 1')
    s3_client.put_object(Bucket=bucket_name, Key='Works/23/W123/images/W123-I1/010.jpg', Body=b'Test Data 2')

    download_and_save_image(bucket_name, obj_dict, save_path)
    
    assert (save_path / '009.jpg').exists()
    assert (save_path / '010.jpg').exists()

if __name__ == "__main__":
    pytest.main()
