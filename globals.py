from yaml import safe_load
from pathlib import Path
import os


DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')

CHALLENGES = {}
dirs = [dir.name for dir in os.scandir(os.path.join(Path(__file__).parent.resolve(), 'challenges'))]
for dir_name in dirs:
    with open(os.path.join(Path(__file__).parent.resolve(), f'challenges/{dir_name}/{dir_name}.yaml'), 'r') as f:
        challenge = safe_load(f)

    if DEPLOYMENT_TYPE is None:
        path_to_file = os.path.join(Path(__file__).parent.resolve(),
                                    f'challenges/{dir_name}/environment/prod/cloud.yaml')
    elif DEPLOYMENT_TYPE == 'DEV':
        path_to_file = os.path.join(Path(__file__).parent.resolve(),
                                    f'challenges/{dir_name}/environment/dev/cloud.yaml')
    else:
        raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

    with open(path_to_file, 'r') as f:
        CLOUD = safe_load(f)

    # Render templates

    # Prize
    challenge['prize']['assign_prizes_source_uri'] = challenge['prize']['assign_prizes_source_uri']\
        .replace("{{ data_bucket }}", CLOUD['bucket'])
    challenge['prize']['build_metamodel']['destination_uri'] = challenge['prize']['build_metamodel']['destination_uri']\
        .replace("{{ data_bucket }}", CLOUD['bucket'])
    challenge['prize']['build_metamodel']['sources']['predictions_uri'] = \
        challenge['prize']['build_metamodel']['sources']['predictions_uri'].replace("{{ data_bucket }}", CLOUD['bucket'])
    challenge['prize']['build_metamodel']['sources']['active_users_uri'] = \
        challenge['prize']['build_metamodel']['sources']['active_users_uri'].replace("{{ data_bucket }}", CLOUD['bucket'])

    # Inference
    challenge['inference']['metamodel_data_gcs_path'] = \
        challenge['inference']['metamodel_data_gcs_path'].replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['inference_data_gcs_path'] = \
        challenge['inference']['inference_data_gcs_path'].replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['logs_data_gcs_path'] = \
        challenge['inference']['logs_data_gcs_path'].replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['bucket'] = \
        challenge['inference']['bucket'].replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['active_user_destination_uri'] = \
        challenge['inference']['active_user_destination_uri'].replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['reset_submission_active_users_uri'] = \
        challenge['inference']['reset_submission_active_users_uri'].replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['build_metamodel']['destination_uri'] = \
        challenge['inference']['build_metamodel']['destination_uri'].replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['build_metamodel']['sources']['predictions_uri'] = \
        challenge['inference']['build_metamodel']['sources']['predictions_uri']\
            .replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['build_metamodel']['sources']['active_users_uri'] = \
        challenge['inference']['build_metamodel']['sources']['active_users_uri']\
            .replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['score_metamodel']['inference_dir'] = \
        challenge['inference']['score_metamodel']['inference_dir']\
            .replace("{{ bucket_name }}", CLOUD['bucket'])
    challenge['inference']['score_metamodel']['metamodel_dir'] = \
        challenge['inference']['score_metamodel']['metamodel_dir'].replace("{{ bucket_name }}", CLOUD['bucket'])

    CHALLENGES[dir_name] = {**challenge, **CLOUD}
