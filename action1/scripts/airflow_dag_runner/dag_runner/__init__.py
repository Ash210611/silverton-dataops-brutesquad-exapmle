import argparse

from .airflow_operator import AirflowOperator, DagMonitorResult


def result_message(result: DagMonitorResult) -> str:
    response_message = {
        DagMonitorResult.SUCCESS: "Dag ran successfully",
        DagMonitorResult.FAILED: "Dag run failed",
        DagMonitorResult.TIMEOUT: "Dag run timed out",
        DagMonitorResult.SERVER_ERROR: "An internal server error occurred",
    }
    return response_message.get(result, "Unrecognized response")


def trigger_dag():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mwaa_env", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--dag_id", required=True)
    parser.add_argument("--s3_path", required=True)
    parser.add_argument("--bucket_env", required=True)
    parser.add_argument("--secrets_manager_name", required=True)
    parser.add_argument("--liquibase_cmd", required=True)

    args = parser.parse_args()

    airflow_operator = AirflowOperator(mwaa_env=args.mwaa_env, region=args.region)
    result = airflow_operator.trigger_dag(
        dag_id=args.dag_id,
        s3_path=args.s3_path,
        bucket_env=args.bucket_env,
        secrets_manager_name=args.secrets_manager_name,
        liquibase_cmd=args.liquibase_cmd,
    )

    if not result:
        exit(1)

    print(f"Dag successfully triggered at {result}")


def trigger_dag_and_monitor():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mwaa_env", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--dag_id", required=True)
    parser.add_argument("--s3_path", required=True)
    parser.add_argument("--bucket_env", required=True)
    parser.add_argument("--secrets_manager_name", required=True)
    parser.add_argument("--liquibase_cmd", required=True)
    parser.add_argument("--wait_time", required=False)

    args = parser.parse_args()

    airflow_operator = AirflowOperator(mwaa_env=args.mwaa_env, region=args.region)
    trigger_result = airflow_operator.trigger_dag(
        dag_id=args.dag_id,
        s3_path=args.s3_path,
        bucket_env=args.bucket_env,
        secrets_manager_name=args.secrets_manager_name,
        liquibase_cmd=args.liquibase_cmd,
    )

    if not trigger_result:
        exit(1)

    print(f"Dag successfully triggered at {trigger_result}")

    try:
        wait_limit = int(args.wait_time)
    except ValueError:
        print("Error: WAIT_TIME parameter must be an integer.")
        raise

    monitor_result = airflow_operator.monitor_dag_run(
        dag_id=args.dag_id, execution_date=trigger_result, check_limit=wait_limit
    )

    print(result_message(monitor_result))

    if monitor_result is not DagMonitorResult.SUCCESS:
        exit(1)


def unpause_dag():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mwaa_env", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--dag_id", required=True)

    args = parser.parse_args()

    airflow_operator = AirflowOperator(mwaa_env=args.mwaa_env, region=args.region)
    airflow_operator.unpause_dag(dag_id=args.dag_id)
