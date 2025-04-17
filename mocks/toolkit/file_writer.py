
def write_file(project_id, file_path, content):
    print(f"Mock: write_file called with project_id={project_id}, file_path={file_path}")
    return {"status": "success", "file_path": file_path}
