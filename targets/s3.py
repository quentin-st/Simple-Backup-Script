from datetime import datetime, timezone, timedelta
import traceback

from utils.stdio import CRESET, CBOLD, LGREEN, ProgressPercentage, CDIM


def get_main_class():
    return S3


class S3:
    def copy_to_target(self, config, target, local_filepath, target_filename):
        import boto3
        from botocore.exceptions import ClientError

        bucket = target.get('bucket')
        profile = target.get('profile', 'default')

        print('')

        session = boto3.Session(profile_name=profile)
        s3_client = session.client('s3')
        try:
            print(CBOLD + LGREEN, "Starting transfer: {} => {}".format(local_filepath, target_filename), CRESET)
            s3_client.upload_file(
                local_filepath, bucket, target_filename,
                Callback=ProgressPercentage(local_filepath),
            )
        except ClientError as e:
            print(CBOLD, "Exception while attempting to transfer file to S3 bucket:", CRESET)
            print(traceback.format_exc())
            return e, traceback

        print('')
        print(CBOLD + LGREEN, "Transfer finished.", CRESET)

        self.rotate_backups(config, target, s3_client)


    def rotate_backups(self, config, target, s3_client):
        days_to_keep = target.get('days_to_keep', config['days_to_keep'])
        bucket = target.get('bucket')

        if days_to_keep == -1:
            return

        now = datetime.now(timezone.utc)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        print(CDIM, 'Deleting files older than {}'.format(str(cutoff_date)), CRESET)

        # List objects
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix='')

        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                last_modified = obj['LastModified']

                if key.startswith('backup-'):
                    delta = now - last_modified

                    if delta.days > days_to_keep:
                        print(CBOLD + LGREEN, "Deleting backup file {key} ({days} days old)".format(
                            key=key, days=delta
                        ), CRESET)
                        s3_client.delete_object(Bucket=bucket, Key=key)
