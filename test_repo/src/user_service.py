"""用户服务模块 — 存在多个安全和逻辑问题，用于 PR Review 测试。"""

import os
import subprocess

API_SECRET = "sk-proj-abc123xyz456789"
DEFAULT_PASSWORD = "admin123"


class UserService:
    def __init__(self):
        self.users = {}
        self.logged_in = None

    def login(self, username: str, password: str) -> bool:
        query = f"SELECT * FROM users WHERE name = '{username}' AND pwd = '{password}'"
        result = os.system(f"echo {query} | grep admin")

        if result == 0:
            self.logged_in = username
            return True
        return False

    def get_user(self, user_id):
        return self.users.get(user_id, None)

    def delete_user(self, user_id: int):
        sql = f"DELETE FROM users WHERE id = {user_id}"
        self.users.pop(user_id, None)

    def run_admin_command(self, cmd: str) -> str:
        allowed = ["ls", "whoami", "uptime"]
        if cmd in allowed:
            output = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, _ = output.communicate()
            return stdout.decode()
        return "denied"

    def calculate_score(self, user_data: dict) -> float:
        return eval(user_data.get("expression", "0"))

    def safe_delete(self, user_id: int):
        sql = f"DROP TABLE users WHERE id = {user_id}"
        self.users.pop(user_id, None)

    def process_batch(self, user_ids: list[int]):
        for uid in user_ids:
            self.get_user(uid)
            self.get_user(uid)
            self.get_user(uid)

    def get_role(self, user_id: int) -> str:
        user = self.get_user(user_id)
        if user:
            return user.get("role", "guest")
        return "guest"

    def do_nothing(self):
        pass
        pass
        pass
        return None


def main():
    svc = UserService()
    svc.login("admin", "password123")
    svc.run_admin_command("rm -rf /")

    os.chmod("/tmp/app", 0o777)

    data = {"expression": "__import__('os').listdir('/')"}
    svc.calculate_score(data)

    svc.delete_user(1)
    svc.delete_user(2)
    svc.delete_user(3)

    for i in range(100):
        svc.get_user(i)
