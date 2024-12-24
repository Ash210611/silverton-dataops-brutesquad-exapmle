import base64
from enum import Enum
from unittest import mock, TestCase
from unittest.mock import patch

import requests_mock

from dag_runner import AirflowOperator, DagMonitorResult


class ResponseType(Enum):
    (
        successful_state,
        unsuccessful_state,
        running_state,
        errored_state,
        successful_dag_trigger,
        successful_dag_trigger_table_format,
        unsuccessful_dag_trigger,
        successful_unpause,
        unsuccessful_unpause,
    ) = range(0, 9)


def base_64_encode_cmd_return(data: dict):
    data["stdout"] = base64.b64encode(data["stdout"].encode("utf-8")).decode()
    data["stderr"] = base64.b64encode(data["stderr"].encode("utf-8")).decode()
    return data


def mock_response(response_type: ResponseType):
    test = {
        ResponseType.successful_state: {"stdout": "success", "stderr": ""},
        ResponseType.unsuccessful_state: {"stdout": "failed", "stderr": ""},
        ResponseType.running_state: {"stdout": "running", "stderr": ""},
        ResponseType.errored_state: {
            "stdout": "",
            "stderr": "Broken DAG: [Errno 2] No such file or directory: "
            "'/usr/local/airflow/dags/invalid_dag_id.py'",
        },
        ResponseType.successful_dag_trigger: {
            "stdout": "Created <DagRun ddl_liquibase @ 2024-01-25T12:15:10+00:00: manual__2024-01-25T12:15:10+00:00, "
            "externally triggered: True>",
            "stderr": "",
        },
        ResponseType.successful_dag_trigger_table_format: {
            "stdout": "|                   |                             |         |\n"
            "| dag_id            | logical_date                | state   |\n"
            "|===================|=======================|=========|\n"
            "| example_dag       | 2024-04-17T18:33: | queued  |\n"
            "|                   | 40+00:00          |         |",
            "stderr": "",
        },
        ResponseType.unsuccessful_dag_trigger: {
            "stdout": "",
            "stderr": "Broken DAG: [Errno 2] No such file or directory: '/usr/local/airflow/dags/invalid_dag_id.py'",
        },
        ResponseType.successful_unpause: {"stdout": "DAG unpaused", "stderr": ""},
        ResponseType.unsuccessful_unpause: {
            "stdout": "",
            "stderr": "DAG not found or already unpaused",
        },
    }
    return base_64_encode_cmd_return(test[response_type])


class TestAirflowOperator(TestCase):
    @mock.patch("boto3.Session")
    def setUp(self, mock_boto_session):
        self.test_server_host = "test.server.com"
        self.server = f"https://{self.test_server_host}/aws_mwaa/cli"
        mock_boto_session().client().create_cli_token.return_value = {
            "CliToken": "mock_token",
            "WebServerHostname": self.test_server_host,
        }
        self.region = "us-east-1"
        self.airflow_operator = AirflowOperator("aae-usmed-airflow-test", self.region)

    @requests_mock.Mocker()
    def test_trigger_dag_success(self, requests_mock):
        requests_mock.post(
            self.server, json=mock_response(ResponseType.successful_dag_trigger)
        )

        dag_id = "ddl_liquibase"
        s3_path = "s3://test-bucket/test-path"
        bucket_env = "test"
        secrets_manager_name = "test_sm_name"
        liquibase_cmd = "update"

        execution_date = self.airflow_operator.trigger_dag(
            dag_id, s3_path, bucket_env, secrets_manager_name, liquibase_cmd
        )

        self.assertEqual(execution_date, "2024-01-25T12:15:10+00:00")

        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body,
            (
                f'dags trigger {dag_id} --conf \'{{"s3_path": "{s3_path}", "bucket_env": "{bucket_env.upper()}", '
                f'"liquibase_cmd": "{liquibase_cmd}", '
                f'"secrets_manager_name": "{secrets_manager_name}", "region": "{self.region}"}}\' '
            ),
        )

    @requests_mock.Mocker()
    def test_trigger_dag_success_table_format(self, requests_mock):
        requests_mock.post(
            self.server,
            json=mock_response(ResponseType.successful_dag_trigger_table_format),
        )

        dag_id = "example_dag"
        s3_path = "s3://test-bucket/test-path"
        bucket_env = "test"
        secrets_manager_name = "test_sm_name"
        liquibase_cmd = "update"

        execution_date = self.airflow_operator.trigger_dag(
            dag_id, s3_path, bucket_env, secrets_manager_name, liquibase_cmd
        )

        self.assertEqual(execution_date, "2024-04-17T18:33:40+00:00")

        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        expected_body = (
            f'dags trigger {dag_id} --conf \'{{"s3_path": "{s3_path}", "bucket_env": "{bucket_env.upper()}", '
            f'"liquibase_cmd": "{liquibase_cmd}", '
            f'"secrets_manager_name": "{secrets_manager_name}", "region": "{self.region}"}}\' '
        )
        self.assertEqual(requests_mock.request_history[0].body, expected_body)

    @requests_mock.Mocker()
    def test_trigger_dag_invalid_dag_id(self, requests_mock):
        requests_mock.post(
            self.server, json=mock_response(ResponseType.unsuccessful_dag_trigger)
        )

        dag_id = "invalid_dag_id"
        s3_path = "s3://test-bucket/test-path"
        bucket_env = "test"
        secrets_manager_name = "test_sm_name"
        liquibase_cmd = "update"

        execution_date = self.airflow_operator.trigger_dag(
            dag_id, s3_path, bucket_env, secrets_manager_name, liquibase_cmd
        )

        self.assertIsNone(execution_date)

        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body,
            (
                f'dags trigger {dag_id} --conf \'{{"s3_path": "{s3_path}", "bucket_env": "{bucket_env.upper()}", '
                f'"liquibase_cmd": "{liquibase_cmd}", '
                f'"secrets_manager_name": "{secrets_manager_name}", "region": "{self.region}"}}\' '
            ),
        )

    @requests_mock.Mocker()
    def test_unpause_dag_success(self, requests_mock):
        requests_mock.post(
            self.server, json=mock_response(ResponseType.successful_unpause)
        )

        dag_id = "ddl_liquibase"

        result = self.airflow_operator.unpause_dag(dag_id)

        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body, f"dags unpause {dag_id}"
        )
        self.assertTrue(result)

    @requests_mock.Mocker()
    def test_unpause_dag_failure(self, requests_mock):
        requests_mock.post(
            self.server, json=mock_response(ResponseType.unsuccessful_unpause)
        )

        dag_id = "ddl_liquibase"
        result = self.airflow_operator.unpause_dag(dag_id)

        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body, f"dags unpause {dag_id}"
        )
        self.assertFalse(result)

    @requests_mock.Mocker()
    def test_monitor_dag_run_success(self, requests_mock):
        requests_mock.post(
            self.server, json=mock_response(ResponseType.successful_state)
        )

        dag_id = "ddl_liquibase"
        execution_date = "2024-01-29"

        result = self.airflow_operator.monitor_dag_run(dag_id, execution_date)

        self.assertEqual(result, DagMonitorResult.SUCCESS)
        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body,
            f"dags state {dag_id} {execution_date}",
        )

    @requests_mock.Mocker()
    def test_monitor_dag_run_failed(self, requests_mock):
        requests_mock.post(
            self.server, json=mock_response(ResponseType.unsuccessful_state)
        )

        dag_id = "ddl_liquibase"
        execution_date = "2024-01-29"

        result = self.airflow_operator.monitor_dag_run(dag_id, execution_date)

        self.assertEqual(result, DagMonitorResult.FAILED)
        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body,
            f"dags state {dag_id} {execution_date}",
        )

    @requests_mock.Mocker()
    @patch("time.sleep", return_value=None)
    def test_given_job_execution_when_monitor_dag_is_run_exceeds_timeout_then_returns_false(
        self, requests_mock, time_sleep
    ):
        requests_mock.post(self.server, json=mock_response(ResponseType.running_state))

        dag_id = "ddl_liquibase"
        execution_date = "2024-01-29"

        result = self.airflow_operator.monitor_dag_run(dag_id, execution_date)

        self.assertEqual(result, DagMonitorResult.TIMEOUT)
        self.assertEqual(time_sleep.call_count, 10)
        self.assertEqual(requests_mock.call_count, 10)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body,
            f"dags state {dag_id} {execution_date}",
        )

    @requests_mock.Mocker()
    def test_monitor_dag_run_error(self, requests_mock):
        requests_mock.post(self.server, json=mock_response(ResponseType.errored_state))

        dag_id = "ddl_liquibase"
        execution_date = "2024-01-29"

        result = self.airflow_operator.monitor_dag_run(dag_id, execution_date)

        self.assertEqual(result, DagMonitorResult.SERVER_ERROR)
        self.assertEqual(requests_mock.call_count, 1)
        self.assertEqual(requests_mock.request_history[0].url, self.server)
        self.assertEqual(
            requests_mock.request_history[0].body,
            f"dags state {dag_id} {execution_date}",
        )
