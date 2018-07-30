Usually , if you have a versioned bucket with objects in it , it's hard to delete the bucket with a simple CLI command or a boto command.

Use this resuable script to achieve deletion of a versioned bucket. Replace bucket-name with the name of your bucket. 

```console
python delete-versioned-bucket.py bucket-name
```


