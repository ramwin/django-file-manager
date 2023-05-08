# django-file-manager
manage your file with a django app. It can remove the duplicate file

# Usage

## init a folder
```
python3 manage.py init_folder <your directory>
```

## scan file in folder, store info in File model
```
python3 manage.py scan_folder
```

## add md5 to file (who has same size)
```
python3 manage.py update_md5_in_need
```

## delete duplicate file
```
python3 manage.py delete_duplicate
```
