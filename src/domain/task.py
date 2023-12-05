# domain/task.py
class Task:
    def __init__(self, user_id, server_id, task_id, task_title, task_detail, task_status, task_color):
        self.user_id = user_id
        self.server_id = server_id
        self.task_id = task_id
        self.task_title = task_title
        self.task_detail = task_detail
        self.task_status = task_status
        self.task_color = task_color

