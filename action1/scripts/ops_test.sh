#!/usr/bin/env bash
set -ex

source commands/test_funcs.sh

pwd

export PATH=$HOME/.local/bin:$PATH

test_individual_module scripts/toml_utilities
test_individual_module scripts/airflow_dag_runner
