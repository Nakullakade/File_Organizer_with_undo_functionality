#!/usr/bin/env python3
from pathlib import Path
import shutil
import json

home_dir=Path.home()
dir_to_organize=home_dir/"organized_directory"
config_file=Path(__file__).parent/"file_categories.json"
undo_log_file=Path(__file__).parent/"undo_log.json"

#load configuration file from json
def get_config_file(config_file):
    if config_file.exists():
       with open(config_file,"r") as file:
            return json.load(file)
    else:
        print("No Config File Found :(")
        return {}

#to get category of each files
def get_categories(file,categories):
    for category,extension in categories.items():
        if file.suffix.lower() in extension:
           return category
    return "Other"

#renaming the files if same file is there in destination
def rename_file(file,directory):
    file_name=file.stem
    file_extension=file.suffix
    new_file=directory/f"{file_name}{file_extension}"
    counter=1
    while new_file.exists():
          new_name=f"{file_name}_{counter}{file_extension}"
          new_file=directory/new_name
          counter+=1
    return new_file

#to get log for movement of the file
def get_log_movement(source,destination):
    if not undo_log_file.exists():
          with open(undo_log_file,'w') as file:
               json.dump({},file)
   try:
        with open(undo_log_file,'r') as file:
             undo_log=json.load(file)
             if not isinstance(undo_log_file,dict):
                    undo_log={}
    except (FileNotFoundError,json.JSONDecodeError):
             undo_log={}

    undo_log[str(destination)]=str(source)
    with open(undo_log_file,'w') as file:
         json.dump(undo_log,file,indent=4)

#to organize the files according to their extension
def organize_files(source_dir,destin_dir,categories):
    if not destin_dir.exists():
       destin_dir.mkdir(parents=True,exist_ok=True)

    if destin_dir.exists():
       for file in source_dir.iterdir():
           if file.is_file():
              category=get_categories(file,categories)
              category_folder=destin_dir/category
              category_folder.mkdir(exist_ok=True)
              new_file_name=rename_file(file,category_folder)
              get_log_movement(file,new_file_name)
              shutil.move(str(file),
                              str(new_file_name))
              print(f"Moved:{new_file_name.stem}->{category_folder}")

#to undo the performed move operation
def undo_last_operation():
    if not Path(undo_log_file).exists():
        print("No log file for undo")
        return

    try:
        # Load the undo log file
        with open(undo_log_file, 'r') as file:
            undo_log = json.load(file)

        # Iterate through each source and destination in the log
        for dst,src in undo_log.items():
            source_path = Path(src)
            destin_path = Path(dst)

            # Check if destination path exists
            if not destin_path.parent.exists():
                print(f"Destination path {destin_path} does not exist, making")
                destin_path.parent.mkdir(parents=True, exist_ok=True)
                continue

            # Ensure the parent directory of the source path exists
            if not source_path.parent.exists():
                try:
                    source_path.parent.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    print("Unable to create directory, skipping")
                    continue

            # Attempt to move the file back to its original location
            try:
                shutil.move(str(destin_path), str(source_path))
                print(f"Moved back {destin_path.name} --> {source_path}")
            except Exception as e:
                print(f"Failed to move back {destin_path.name}, reason -> {e}")
                continue

        # Clear the undo log after all operations
        try:
            Path(undo_log_file).unlink()
            print("Cleared undo log file")
        except Exception as e:
            print(f"Failed to clear undo log, reason -> {e}")

        print("Undo completed!")

    except json.JSONDecodeError:
        print("Undo log is corrupted")

    except Exception as e:
        print(f"An unexpected error occurred, reason -> {e}")

#main function
if __name__ == "__main__":
   import sys
   try:
       if len(sys.argv)>1 and sys.argv[1]=="undo":
          undo_last_operation()
       else:
           custom_config=get_config_file(config_file)
           organize_files(home_dir,dir_to_organize,custom_config)

   except FileNotFoundError as e:
          print(e)
