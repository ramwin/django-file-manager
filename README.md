# django-file-manager
manage your file with a django app. It can remove the duplicate file

# Features
* [x] backup multi directory
* [x] delete duplicate file(by md5)

# Usage

## download
```
git clone git@github.com:ramwin/django-file-manager.git
cd django-file-manager
pip install -r ./requirements.txt
python3 manage.py migrate
```

## init a folder
```
python3 manage.py init_folder <your directory>
python3 manage.py init_folder <another directory>  # you can add multi foler
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
python3 manage.py delete_duplicate --no-act # check before you delete your file
python3 manage.py delete_duplicate
```
