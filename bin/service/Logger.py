from bin.service import Environment
import datetime


class Logger:

    @staticmethod
    def add_entry(code_reference, message):
        environment = Environment.Environment()
        log_file = environment.get_path_log()
        now = datetime.datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        entry = "{}: {} - {}\n".format(current_time, code_reference, message)
        file = open(log_file, "a")
        file.write(entry)
        file.close()

    @staticmethod
    def get_latest_entries(line_count):
        environment = Environment.Environment()
        log_file = environment.get_path_log()
        file = open(log_file, "r")
        content = file.read()
        file.close()
        lines = content.splitlines()
        return lines[-line_count:]
