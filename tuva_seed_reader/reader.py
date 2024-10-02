"""Reads Tuva S3 Files for Postgres"""
import boto3
import sys
import typer
from smart_open import open


def parse_uri(uri:str) -> tuple[str,str]: 
    """ Parses the uri into bucket base and object path to find the csv files.

        Args:
            uri: string the is in the format 'bucket/path/to/object'

        Returns:
            Two string the first is the bucket_name
            the second is the object_path used to filter by prefix
    """
    parse_list = uri.split("/",1)
    return parse_list[0],parse_list[1]

def get_bucket_contents(client,bucket:str,prefix:str) -> dict:
    """ Obtains all the contents in the bucket filtered by prefix

        Args:
            client: S3 client object connected to tuva S3 bucket.
            bucket: The name of the tuva bucket to search.
            prefix: Object path used to fileter the bucket search.

        Returns:
            The "Contents" section of the result in a dictionary format or None
    """
    result = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return result.get("Contents",{})

def get_s3_objs_by_pattern(contents:dict,pattern:str) -> list[str]:
    """Find all the objects that match the pattern in the bucket contents dictionary.
    
        Args:
            contents: Dictionary containing the buckets contents info to search.
            pattern: The key pattern of the csv file to seach for.
        
        Returns:
            A list of files found that matched the pattern.
    """
    result_list = []
    for obj in contents:
        if str(obj["Key"]).startswith(pattern):
                result_list.append(obj)
    return result_list 

def main(uri:str, pattern:str)  -> None:
    """Main loop that does the following.
        
        1. Creats a S3 Client object with the Tuva access info.
        2. Parses the URI given to pass to other function.
        3. Obtains the contents of the bucket filtered to a specific path.
        4. Finds all the files that match the pattern in the contents and
           writes there contents out to stdout. 
    
    """
    # AWS S3 client object to be used
    tuva_s3_client = boto3.client(
        service_name="s3",
    )

    # Populate variable neccary to read the contents of the Tuva seed files.
    bucket_name,object_path = parse_uri(uri=uri)
    key_pattern = f"{object_path}/{pattern}"
    bucket_contents = get_bucket_contents(tuva_s3_client,bucket=bucket_name,prefix=object_path)
    
    # Read the contents of the Tuva seed files passing the stdout so COPY FROM PROGRAM grab them.
    for obj in get_s3_objs_by_pattern(contents=bucket_contents,pattern=key_pattern):
        for line in open(f"s3://{bucket_name}/{obj['Key']}",mode="rb",transport_params={"client":tuva_s3_client}):
            sys.stdout.buffer.write(line.replace(b'"\\N"',b''))
            sys.stdout.flush()  

def typer_run_main() -> None:
    """Wrapper function to allow main to be stared by Typer."""
    typer.run(main)

if __name__ == "__main__":
    typer_run_main
