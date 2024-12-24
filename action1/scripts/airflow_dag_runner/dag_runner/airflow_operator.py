import base64
import re
import time
from enum import Enum
from io import StringIO
from typing import Tuple, Union

import boto3
import pandas as pd
import requests


class DagMonitorResult(Enum):
    (SUCCESS, FAILED, SERVER_ERROR, TIMEOUT) = range(0, 4)


def _parse_response(response: requests.Response) -> Tuple[str, str]:
    stdout_decoded, stderr_decoded = "", ""
    try:
        response_json = response.json()
        stdout = response_json["stdout"]
        stderr = response_json["stderr"]
        stdout_decoded = base64.b64decode(stdout).decode()
        stderr_decoded = base64.b64decode(stderr).decode()
    except Exception as e:
        print(f"An error occurred while parsing response: {e}")
        stdout_decoded = str(response.status_code)
        stderr_decoded = response.text
    finally:
        return stdout_decoded, stderr_decoded


def _parse_dag_trigger_response_for_execution_date(
    trigger_stdout: str,
) -> Union[str, None]:
    if "Created" in trigger_stdout:
        match = re.search(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}", trigger_stdout
        )
        if match:
            return match.group()

    else:
        try:
            df = pd.read_csv(
                StringIO(trigger_stdout), sep="|", engine="python", skiprows=1, header=0
            )
            df.dropna(axis=1, how="all", inplace=True)
            df.dropna(axis=0, how="all", inplace=True)
            df.reset_index(drop=True, inplace=True)
            for col in df.columns:
                if "logical_date" in col:
                    execution_date = df[col].iloc[1].strip() + df[col].iloc[2].strip()
                    return execution_date.strip()
        except Exception as e:
            print(f"An error occurred while parsing the execution date: {e}")

    return None


def _get_client(region: str):
    session = boto3.Session(region_name=region, profile_name="saml")
    return session.client("mwaa")


class AirflowOperator:
    def __init__(self, mwaa_env: str, region: str = "us-east-1") -> None:
        self.mwaa_env = mwaa_env
        self.region = region
        self.client = _get_client(region)
        self.cli_token, self.web_server_hostname = self._get_cli_token_and_hostname()

    def _get_cli_token_and_hostname(self) -> Tuple[str, str]:
        cli_dict = self.client.create_cli_token(Name=self.mwaa_env)
        cli_token = cli_dict["CliToken"]
        web_server_hostname = cli_dict["WebServerHostname"]
        return cli_token, web_server_hostname

    def _send_post_request(self, airflow_command: str) -> requests.Response:
        url = f"https://{self.web_server_hostname}/aws_mwaa/cli"
        headers = {
            "Authorization": f"Bearer {self.cli_token}",
            "Content-Type": "text/plain",
        }
        data = airflow_command
        response = requests.post(url, data=data, headers=headers)
        return response

    def trigger_dag(
        self, dag_id: str, s3_path: str, bucket_env: str, secrets_manager_name: str, liquibase_cmd: str = "update",
    ) -> Union[str, None]:
        airflow_trigger_command = (
            f'dags trigger {dag_id} --conf \'{{"s3_path": "{s3_path}", "bucket_env": "{bucket_env.upper()}", '
            f'"liquibase_cmd": "{liquibase_cmd}", '
            f'"secrets_manager_name": "{secrets_manager_name}", "region": "{self.region}"}}\' '
        )
        trigger_response = self._send_post_request(airflow_trigger_command)
        trigger_stdout, trigger_stderr = _parse_response(trigger_response)
        if trigger_stdout.startswith("Created") or "queued" in trigger_stdout.lower():
            execution_date = _parse_dag_trigger_response_for_execution_date(
                trigger_stdout
            )
            return execution_date
        else:
            print(f"Error triggering DAG: {trigger_stderr}")
            return None

    def unpause_dag(self, dag_id: str) -> bool:
        airflow_unpause_command = f"dags unpause {dag_id}"
        unpause_response = self._send_post_request(airflow_unpause_command)
        unpause_stdout, unpause_stderr = _parse_response(unpause_response)
        if unpause_stderr:
            print(f"Error: {unpause_stderr}")
            return False
        return True

    def monitor_dag_run(
        self,
        dag_id: str,
        execution_date: str,
        check_limit: int = 10,
        wait_time: int = 60,
    ) -> DagMonitorResult:
        counter = 0
        while counter < check_limit:
            airflow_state_command = f"dags state {dag_id} {execution_date}"
            state_response = self._send_post_request(airflow_state_command)
            state_stdout, state_stderr = _parse_response(state_response)

            if state_stdout.startswith("running"):
                print("Waiting some more...")
                time.sleep(wait_time)
                self.cli_token, self.web_server_hostname = self._get_cli_token_and_hostname()
                counter += 1
            elif state_stdout.startswith("success"):
                return DagMonitorResult.SUCCESS
            elif state_stdout.startswith("failed"):
                print("STDOUT:::", state_stdout)
                print("STDERR:::", state_stderr)
                return DagMonitorResult.FAILED
            else:
                print("STDOUT:::", state_stdout)
                print("STDERR:::", state_stderr)
                return DagMonitorResult.SERVER_ERROR

        return DagMonitorResult.TIMEOUT
