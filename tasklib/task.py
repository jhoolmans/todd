import re
import datetime
from tasklib import Util


class Task:
    """Task

    Format:
    x (A) 2000-01-01 2000-01-01 DESC

    DESC may contain
    - text
    - +TAG              tags
    - @CONTEXT          contexts
    - KEY:VALUE         special key-value tag

    Know key-value tags are
    - due:2000-01-01    due dates
    - rec:1y            recurring task
    """

    _priority_regex = re.compile(r"\(([A-Z])\) ")
    _context_regex = re.compile(r"(?:^|\s+)(@\S+)")
    _project_regex = re.compile(r"(?:^|\s+)(\+\S+)")
    _done_regex = re.compile(r"^x (\d\d\d\d-\d\d-\d\d) ")

    _creation_date_prefix = (
        r"^"
        r"(x \d\d\d\d-\d\d-\d\d\s+)?"
        r"(\(\w\)\s+)?")
    _creation_date_regex = re.compile(
        _creation_date_prefix +
        r"(\d\d\d\d-\d\d-\d\d)\s*")
    _creation_date_regex2 = re.compile(
        _creation_date_prefix)
    _due_date_regex = re.compile(r"\s*due:(\d\d\d\d-\d\d-\d\d)\s*")
    _rec_int_regex = re.compile(r"\s*rec:(\+?\d+[dwmy])\s*")
    _rec_int_parts_regex = re.compile(r"(\+)?(\d+)([dwmy])")

    PLHR = u"\N{HORIZONTAL ELLIPSIS}"
    _plhr_regex = re.compile(PLHR + "[ " + PLHR + "]*")

    def __init__(self, item, task_id):
        self.task_id = task_id
        self.update(item)

    def update(self, text):
        self.raw = text.strip()
        self.priority = Task.scan_priority(self.raw)
        self.contexts = Task.scan_contexts(self.raw)
        self.projects = Task.scan_projects(self.raw)
        self.done_date = Task.scan_done_date(self.raw)
        self.creation_date = Task.scan_creation_date(self.raw)
        self.due_date = Task.scan_due_date(self.raw)
        self.rec_int = Task.scan_rec_int(self.raw)

    @staticmethod
    def scan_contexts(text):
        return sorted(Task._context_regex.findall(text))

    @staticmethod
    def scan_projects(text):
        return sorted(Task._project_regex.findall(text))

    @staticmethod
    def scan_creation_date(text):
        match = Task._creation_date_regex.search(text)
        return match.group(3) if match else ""

    @staticmethod
    def scan_due_date(text):
        match = Task._due_date_regex.search(text)
        return match.group(1) if match else ""

    @staticmethod
    def scan_rec_int(text):
        match = Task._rec_int_regex.search(text)
        return match.group(1) if match else ""

    @staticmethod
    def scan_priority(text):
        match = Task._priority_regex.match(text)
        return match.group(1) if match else ""

    @staticmethod
    def scan_done_date(text):
        match = Task._done_regex.match(text)
        return match.group(1) if match else ""

    @staticmethod
    def get_current_date(inc=0):
        return datetime.date.today() + datetime.timedelta(days=inc)

    @staticmethod
    def get_current_date_str(inc=0):
        return Task.get_current_date(inc).isoformat()

    def __repr__(self):
        return repr({
            "raw": self.raw,
            "task_id": self.task_id,
            "priority": self.priority,
            "done_date": self.done_date,
            "creation_date": self.creation_date,
            "contexts": self.contexts,
            "projects": self.projects,
            "due_date": self.due_date,
            "rec_int": self.rec_int,
        })

    def set_priority(self, new_priority):
        if self.priority == new_priority: return
        if new_priority:
            new_priority = "({}) ".format(new_priority)

        # Task
        if re.search(self._priority_regex, self.raw):
            self.raw = re.sub(self._priority_regex, "{}".format(new_priority), self.raw)
        elif re.search(r"^x \d{4}-\d{2}-\d{2}", self.raw):
            self.raw = re.sub(r"^(x \d{4}-\d{2}-\d{2}) ", r"\1 {}".format(new_priority), self.raw)
        else:
            self.raw = "{}{}".format(new_priority, self.raw)
        self.update(self.raw)

    def is_done(self):
        return self.raw[0:2] == "x "

    def set_done(self, done=True):
        if self.is_done() == done: return
        if done:
            self.set_priority("")
            today = datetime.date.today()
            self.update("x " + today.isoformat() + " " + self.raw)
            if self.rec_int:
                (prefix, value, itype) = Task._rec_int_parts_regex.match(self.rec_int).groups()
                value = int(value)
                date = self.get_due() if prefix == "+" else today
                return Util.date_add_interval(date, itype, value)
        else:
            self.update(re.sub(Task._done_regex, "", self.raw))

    def get_status(self, sdate):
        if self.is_done(): return "done"
        if self.due_date:
            if self.due_date < sdate: return "overdue"
            elif self.due_date == sdate: return "due"
        return "todo"

    def is_due(self, sdate):
        return not self.is_done() and self.due_date and self.due_date <= sdate

    def set_due(self, date):
        if type(date) is datetime.datetime: date = date.date()
        text = " due:" + date.isoformat()
        if self.due_date: self.raw = re.sub(Task._due_date_regex, text + " ", self.raw)
        else: self.raw += text
        self.update(self.raw)

    def get_due(self):
        return datetime.datetime.strptime(self.due_date, "%Y-%m-%d").date() if self.due_date else None

    def set_creation_date(self, date):
        if type(date) is datetime.datetime: date = date.date()
        regex = Task._creation_date_regex if self.creation_date != "" else Task._creation_date_regex2
        self.raw = re.sub(regex, r"\g<1>\g<2>" + date.isoformat() + " ", self.raw)
        self.update(self.raw)

    def get_desc(self):
        PLHR = u" \N{HORIZONTAL ELLIPSIS} "
        res = self.raw
        if self.creation_date != '':
            res = re.sub(Task._creation_date_regex, r"\1\2", res)
        res = re.sub(Task._due_date_regex, PLHR, res)
        res = re.sub(Task._rec_int_regex, PLHR, res)
        res = re.sub(Task._context_regex, PLHR, res)
        res = re.sub(Task._plhr_regex, PLHR, res)
        return res.strip(PLHR)
